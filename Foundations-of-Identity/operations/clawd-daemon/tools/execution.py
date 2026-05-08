"""Execution tools — shell, python_eval, manage_process."""
import asyncio
import json
import logging
import os
import re
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import config
from tools._base import resolve_path

logger = logging.getLogger("clawd.tools.execution")

# Failover mode flag — set by ModelRouter when a fallback model is active.
# When True, destructive shell commands are blocked.
_failover_mode = False


def set_failover_mode(enabled: bool):
    """Called by ModelRouter to activate/deactivate destructive-command guardrails."""
    global _failover_mode
    _failover_mode = enabled


# Patterns that are blocked when running under failover mode.
# These cover common destructive commands on both Windows and Unix.
_DESTRUCTIVE_SHELL_PATTERNS = [
    r"taskkill\b",                    # Windows process kill
    r"kill\s+-\d+",                   # Unix kill with signal
    r"kill\s+-[A-Z]+",               # Unix kill -KILL, kill -TERM, etc.
    r"kill\s+\d+",                   # Unix kill <pid>
    r"\brm\s+-[rR]",                 # rm -r / rm -rf
    r"\brmdir\s+/[sS]",             # Windows rmdir /s
    r"\bdel\s+/[fFqQ]",             # Windows del /f /q
    r"\bformat\s+[a-zA-Z]:",        # format C:
    r"\bshutdown\b",                 # system shutdown
    r"\brestart\b.*(?:service|daemon|computer)",
    r"\bnet\s+(?:user|stop)\b",     # Windows net user / net stop
    r"\breg\s+delete\b",            # Windows registry delete
    r"\bdiskpart\b",                 # disk partition tool
    r"\bdd\s+.*of=",                # dd write to device
    r"\bmkfs\b",                     # format filesystem
    r"Stop-Process\b",              # PowerShell process kill
    r"Remove-Item\s.*-Recurse",     # PowerShell recursive delete
]

# Background process tracking (in-memory + persisted to disk)
_background_processes: dict[int, dict] = {}
_BG_PROCS_FILE = Path(config.CLAWD_HOME) / "logs" / "background_processes.json"


def _save_bg_procs():
    """Persist background process tracking info to disk."""
    data = {}
    for pid, info in _background_processes.items():
        data[str(pid)] = {
            "name": info.get("name", ""),
            "command": info.get("command", ""),
            "started": info.get("started", ""),
            "log_file": info.get("log_file", ""),
        }
    try:
        _BG_PROCS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _BG_PROCS_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        logger.warning(f"Failed to save background process tracking: {e}")


def _load_bg_procs():
    """Load persisted process info and recover still-running PIDs."""
    if not _BG_PROCS_FILE.exists():
        return
    try:
        data = json.loads(_BG_PROCS_FILE.read_text())
        for pid_str, info in data.items():
            pid = int(pid_str)
            try:
                os.kill(pid, 0)  # Check if still alive (signal 0)
                _background_processes[pid] = {
                    "proc": None,
                    "name": info.get("name", ""),
                    "command": info.get("command", ""),
                    "started": info.get("started", ""),
                    "log_file": info.get("log_file", ""),
                }
                logger.info(f"Recovered background process: PID {pid} ({info.get('name', '')})")
            except (OSError, ProcessLookupError):
                logger.debug(f"Stale PID {pid} no longer running")
    except Exception as e:
        logger.warning(f"Failed to load background process tracking: {e}")


# Load persisted processes on module import
_load_bg_procs()

# Blocked patterns for python_eval safety
_BLOCKED_PATTERNS = [
    "pip install", "pip uninstall",
    "os.system(", "subprocess.call(", "subprocess.run(",
    "subprocess.Popen(",
    "__import__('os').system",
    "importlib.import_module",
]

TOOL_DEFINITIONS = [
    {
        "name": "shell",
        "description": "Execute any shell command with full administrator access. No restrictions. Use for git, python, node, npm, pip, system commands, process management, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute."
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory. Defaults to CLAWD_HOME."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds. Default: 600."
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "python_eval",
        "description": "Execute Python code with a full scientific computing environment pre-loaded. Pre-imported: numpy (np), pandas (pd), scipy (stats, optimize, signal, fft, linalg, integrate), sympy (symbols, solve, diff, simplify, Matrix, etc), matplotlib (plt), sklearn, statsmodels, networkx, yfinance (yf), ccxt. Helpers: save_plot(filename), save_data(data, filename), quick_stats(data), correlation_matrix(df), get_stock(ticker, period), get_crypto(symbol, exchange, timeframe, limit). Output dir: CLAWD_HOME/output/.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute. Can be multi-line. The last expression's value is captured and returned."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds. Default: 300."
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "code_action",
        "description": "Execute Python code that can call Clawd's tools directly via sync bridge functions. Use for multi-step operations that would otherwise require multiple tool calls. Available functions: shell(command), read_file(path), write_file(path, content), list_directory(path), memory_search(query, strategy='auto', top_k=10), memory_update(target, content), web_request(url, method='GET'), search_web(query), knowledge_graph(action, **kwargs), git(action, **kwargs). Each returns a string result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute. Tool bridge functions are available as sync calls that return strings."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Max execution seconds (default 30, max 120)."
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "evolve_artifact",
        "description": "Evolve a code artifact using EAC (Evolutionary Artifact Construction). Seed new artifacts, mutate existing ones, evaluate fitness, or run crossover between two artifacts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["seed", "mutate", "evaluate", "crossover", "list", "lineage", "stats"],
                    "description": "Action to perform."
                },
                "code": {
                    "type": "string",
                    "description": "Source code (for seed/evaluate)."
                },
                "name": {
                    "type": "string",
                    "description": "Artifact name (for seed)."
                },
                "artifact_type": {
                    "type": "string",
                    "enum": ["tool", "skill", "workflow", "prompt", "config"],
                    "description": "Artifact type. Default: tool."
                },
                "artifact_id": {
                    "type": "string",
                    "description": "Artifact ID (for mutate/evaluate/crossover/lineage)."
                },
                "strategy": {
                    "type": "string",
                    "enum": ["rename", "refactor", "optimize", "simplify", "expand", "comment", "inline", "crossover"],
                    "description": "Mutation strategy (for mutate)."
                },
                "artifact_id_b": {
                    "type": "string",
                    "description": "Second artifact ID (for crossover)."
                },
                "test_input": {
                    "type": "string",
                    "description": "Test input for fitness evaluation."
                },
                "expected_output": {
                    "type": "string",
                    "description": "Expected output for fitness evaluation."
                },
                "parameters": {
                    "type": "object",
                    "description": "Strategy-specific parameters for mutation."
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "manage_process",
        "description": "Start, stop, or check background processes. Use for long-running tasks, servers, watchers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["start", "stop", "list", "check"],
                    "description": "Action to perform."
                },
                "command": {
                    "type": "string",
                    "description": "Command to start (for 'start' action)."
                },
                "pid": {
                    "type": "integer",
                    "description": "Process ID (for 'stop' or 'check' actions)."
                },
                "name": {
                    "type": "string",
                    "description": "Friendly name for the process."
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "wolfram",
        "description": "Execute Wolfram Language code via Wolfram Engine 14.3. Use for: symbolic math, tensor algebra (Christoffel symbols, Riemann tensor, spectral triples), group theory, number theory, differential equations, cellular automata, plotting, Export[] to files. Full Mathematica language.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Wolfram Language code to execute. Use Print[] for output. Use Export[] to save files."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds. Default: 120."
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "wsl",
        "description": "Execute a command in WSL (Ubuntu 22.04 'Clawd' with CUDA passthrough). Use for: GPU-accelerated training/MCMC on Linux, FluidSynth music rendering, any Linux-native tooling. Has PyTorch 2.6+CUDA, CAMB, scipy, numpy, PennyLane. Windows filesystem at /mnt/c/. Set session_name to launch persistent processes via tmux that survive daemon restarts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Bash command to run inside WSL."
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory inside WSL (Linux path). Defaults to home."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds. Default: 600."
                },
                "session_name": {
                    "type": "string",
                    "description": "If set, launches the command in a detached tmux session that persists across daemon restarts. Use for MCMC, training, or any long-running job. Check with wsl(command='tmux ls')."
                }
            },
            "required": ["command"]
        }
    },
]


# === Pre-execution Risk Assessment ===

_HIGH_RISK_PATTERNS = {
    "critical": [
        (r"\brm\s+-rf\s+[/~]", "Recursive force delete from root/home"),
        (r"\bgit\s+push\s+.*--force", "Force push (can destroy remote history)"),
        (r"\bgit\s+reset\s+--hard", "Hard reset (destroys uncommitted changes)"),
        (r"\bDROP\s+(TABLE|DATABASE)\b", "SQL DROP (data destruction)"),
        (r"\bformat\s+[a-zA-Z]:", "Disk format"),
        (r"\bdd\s+.*of=/dev/", "Direct disk write"),
        (r"curl\s+.*\|\s*(ba)?sh", "Pipe remote script to shell"),
        (r"\bnpm\s+publish\b", "Publish to npm (public)"),
        (r"\bdocker\s+system\s+prune\s+-a", "Docker nuke all"),
    ],
    "high": [
        (r"\brm\s+-[rR]", "Recursive delete"),
        (r"\brmdir\s+/[sS]", "Windows recursive directory delete"),
        (r"\bgit\s+push\b", "Push to remote repository"),
        (r"\bgit\s+branch\s+-[dD]\b", "Delete git branch"),
        (r"\bpip\s+install\b", "Install Python package"),
        (r"\bnpm\s+install\b", "Install npm package"),
        (r"\bchmod\s+[0-7]*[0-7]\s", "Change file permissions"),
        (r"\bchown\b", "Change file ownership"),
        (r"TRUNCATE\s+TABLE\b", "SQL truncate"),
        (r"\btaskkill\b", "Kill Windows process"),
    ],
    "medium": [
        (r"\bgit\s+commit\b", "Git commit"),
        (r"\bgit\s+checkout\b", "Git checkout (may lose changes)"),
        (r"\bgit\s+merge\b", "Git merge"),
        (r"\bgit\s+stash\b", "Git stash"),
        (r"\bkill\s+\d+", "Kill process by PID"),
        (r"\bsystemctl\s+(start|stop|restart)\b", "Service management"),
        (r"\bnet\s+(start|stop)\b", "Windows service management"),
        (r"DELETE\s+FROM\b", "SQL delete"),
        (r"UPDATE\s+.*SET\b", "SQL update"),
    ],
}

_RISK_LEVELS = ["low", "medium", "high", "critical"]


def _normalize_command(command: str) -> str:
    """Normalize a shell command for robust pattern matching.
    Collapses whitespace, handles common evasion techniques."""
    # Collapse multiple spaces/tabs to single space
    normalized = re.sub(r'\s+', ' ', command)
    # Remove null bytes and zero-width characters
    normalized = normalized.replace('\x00', '').replace('\u200b', '').replace('\u200c', '')
    return normalized


def assess_command_risk(command: str) -> dict:
    """Pre-execution risk assessment for shell commands.

    Returns:
        {
            "risk_level": "low"|"medium"|"high"|"critical",
            "risks": [{"pattern": ..., "description": ...}],
            "requires_verification": bool,
            "recommendation": str
        }
    """
    risks = []
    max_level = "low"

    # Normalize command to defeat simple evasion (double spaces, null bytes, etc.)
    normalized = _normalize_command(command)

    # Check for command chaining operators that could bypass single-command patterns
    chaining_ops = [';', '&&', '||', '|', '`', '$(']
    chained_parts = [normalized]
    for op in [';', '&&', '||']:
        new_parts = []
        for part in chained_parts:
            new_parts.extend(part.split(op))
        chained_parts = new_parts

    # Assess each chained segment independently
    for segment in chained_parts:
        segment = segment.strip()
        if not segment:
            continue
        for level in ["critical", "high", "medium"]:
            for pattern, description in _HIGH_RISK_PATTERNS.get(level, []):
                if re.search(pattern, segment, re.IGNORECASE):
                    risks.append({"pattern": pattern, "description": description, "level": level})
                    if _RISK_LEVELS.index(level) > _RISK_LEVELS.index(max_level):
                        max_level = level

    result = {
        "risk_level": max_level,
        "risks": risks,
        "requires_verification": max_level in ("high", "critical"),
        "recommendation": "",
    }

    if max_level == "critical":
        result["recommendation"] = "BLOCKED: This command is critically dangerous. Ask Clayton via Telegram before proceeding."
    elif max_level == "high":
        result["recommendation"] = "WARNING: High-risk command. Double-check intent and log to memory audit trail."
    elif max_level == "medium":
        result["recommendation"] = "CAUTION: Moderate-risk command. Verify parameters are correct."
    else:
        result["recommendation"] = "Low risk — proceed normally."

    return result


async def _shell(input_data: dict) -> str:
    command = input_data["command"]

    # Pre-execution risk assessment
    risk = assess_command_risk(command)
    if risk["risk_level"] == "critical":
        logger.warning(f"CRITICAL risk command blocked: {command[:200]}")
        risk_desc = "; ".join(r["description"] for r in risk["risks"])
        return (
            f"[BLOCKED] Critical-risk command detected: {risk_desc}\n"
            f"Recommendation: {risk['recommendation']}\n"
            f"Use send_telegram to ask Clayton for permission."
        )
    elif risk["risk_level"] == "high":
        # Log warning but allow execution
        logger.warning(f"HIGH risk command executing: {command[:200]} — risks: {risk['risks']}")
        try:
            from tools.memory_tools import _memory_update
            await _memory_update({
                "target": "daily_log",
                "content": f"[RISK AUDIT] Executing high-risk command: {command[:100]} — {risk['recommendation']}"
            })
        except Exception as e:
            logger.debug(f"Failed to log high-risk command to memory audit: {e}")
    working_dir = input_data.get("working_dir", str(config.CLAWD_HOME))
    timeout = input_data.get("timeout", config.SHELL_TIMEOUT_SECONDS)

    # Block destructive commands when running under failover mode
    if _failover_mode:
        for pattern in _DESTRUCTIVE_SHELL_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning(
                    f"BLOCKED destructive command in failover mode: {command[:200]}"
                )
                return (
                    f"[BLOCKED] Destructive command rejected during failover mode: "
                    f"'{command[:100]}'. Destructive actions (process killing, file deletion, "
                    f"system modification) are not allowed from fallback models. "
                    f"Please inform the user what you intended to do and let them decide."
                )

    proc = None
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir,
            env={**os.environ, "HOME": str(config.CLAWD_HOME)},
            start_new_session=True,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        result_parts = []
        if stdout:
            out = stdout.decode("utf-8", errors="replace")
            if len(out) > 100_000:
                out = out[:100_000] + "\n[... truncated]"
            result_parts.append(f"STDOUT:\n{out}")
        if stderr:
            err = stderr.decode("utf-8", errors="replace")
            if len(err) > 50_000:
                err = err[:50_000] + "\n[... truncated]"
            result_parts.append(f"STDERR:\n{err}")
        result_parts.append(f"Exit code: {proc.returncode}")
        result_text = "\n".join(result_parts) if result_parts else "Command completed (no output)."

        # Record shell command for rollback tracking
        try:
            from tools.rollback import get_tracker
            get_tracker().record_shell_command(command, working_dir, result_text[:200])
        except Exception as e:
            logger.debug(f"Failed to record shell command for rollback tracking: {e}")

        return result_text
    except asyncio.TimeoutError:
        return f"Command timed out after {timeout}s."
    finally:
        if proc and proc.returncode is None:
            try:
                proc.kill()
                await proc.wait()
            except Exception as e:
                logger.debug(f"Failed to kill shell subprocess during cleanup: {e}")


async def _python_eval(input_data: dict) -> str:
    """Execute Python code with full scientific computing stack pre-loaded."""
    code = input_data["code"]
    timeout = input_data.get("timeout", 300)

    # Safety check: block dangerous patterns
    code_lower = code.lower()
    for pattern in _BLOCKED_PATTERNS:
        if pattern.lower() in code_lower:
            return f"Blocked: '{pattern}' is not allowed in python_eval. Use the shell tool for package management and system commands."

    wrapper = f"""
import sys, io, traceback, os, json, warnings
warnings.filterwarnings('ignore')
os.environ['MPLBACKEND'] = 'Agg'

_stdout = io.StringIO()
_old_stdout = sys.stdout
sys.stdout = _stdout

try:
    import numpy as np
    import pandas as pd
    import scipy
    from scipy import stats, optimize, signal, fft, linalg, integrate
    import sympy as sp
    from sympy import symbols, solve, diff, integrate as sym_integrate, simplify, expand, factor, Matrix, pi, E, oo, sqrt, sin, cos, tan, log, exp, Rational
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    from pathlib import Path
    import math
    import statistics
    import itertools
    import functools
    import collections
    import re
except ImportError as e:
    print(f"Note: {{e}}")

try:
    from sklearn import linear_model, cluster, decomposition, preprocessing, metrics, model_selection, ensemble, svm, neighbors, tree
    from sklearn.pipeline import Pipeline
except ImportError:
    pass
try:
    import statsmodels.api as sm
    import statsmodels.tsa.api as tsa
    from statsmodels.tsa.stattools import adfuller, coint, grangercausalitytests
except ImportError:
    pass
try:
    import networkx as nx
except ImportError:
    pass
try:
    import yfinance as yf
except ImportError:
    pass
try:
    import ccxt
except ImportError:
    pass

CLAWD_HOME = Path({repr(str(config.CLAWD_HOME))})
OUTPUT_DIR = CLAWD_HOME / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

def save_plot(filename='plot.png', dpi=150):
    path = OUTPUT_DIR / filename
    plt.savefig(path, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"Plot saved: {{path}}")
    return str(path)

def save_data(data, filename='data.csv'):
    path = OUTPUT_DIR / filename
    if isinstance(data, pd.DataFrame):
        data.to_csv(path)
    elif isinstance(data, dict):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    else:
        with open(path, 'w') as f:
            f.write(str(data))
    print(f"Data saved: {{path}}")
    return str(path)

def quick_stats(data):
    arr = np.array(data, dtype=float)
    return {{
        'n': len(arr), 'mean': np.mean(arr), 'std': np.std(arr),
        'min': np.min(arr), 'max': np.max(arr),
        'median': np.median(arr), 'skew': float(stats.skew(arr)),
        'kurtosis': float(stats.kurtosis(arr)),
        'q25': np.percentile(arr, 25), 'q75': np.percentile(arr, 75),
    }}

def correlation_matrix(df, method='pearson'):
    corr = df.corr(method=method)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr.columns)
    plt.colorbar(im)
    plt.title(f'Correlation Matrix ({{method}})')
    plt.tight_layout()
    return corr

def get_stock(ticker, period='1y'):
    return yf.download(ticker, period=period, progress=False)

def get_crypto(symbol='BTC/USDT', exchange='binance', timeframe='1d', limit=365):
    ex = getattr(ccxt, exchange)()
    ohlcv = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

try:
    _code = {repr(code)}
    _lines = _code.strip().split('\\n')
    if len(_lines) > 1:
        exec('\\n'.join(_lines[:-1]))
        try:
            _result = eval(_lines[-1])
            if _result is not None:
                print(repr(_result))
        except SyntaxError:
            exec(_lines[-1])
    else:
        try:
            _result = eval(_lines[0])
            if _result is not None:
                print(repr(_result))
        except SyntaxError:
            exec(_lines[0])
except Exception:
    traceback.print_exc()
finally:
    sys.stdout = _old_stdout
    print(_stdout.getvalue(), end='')
"""

    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", wrapper,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(config.CLAWD_HOME),
            start_new_session=True,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        result = stdout.decode("utf-8", errors="replace")
        err = stderr.decode("utf-8", errors="replace")
        parts = []
        if result.strip():
            parts.append(result)
        if err.strip():
            parts.append(f"STDERR:\n{err}")
        parts.append(f"Exit code: {proc.returncode}")
        output = "\n".join(parts)
        if len(output) > 100_000:
            output = output[:100_000] + "\n[... truncated]"
        return output or "Code executed (no output)."
    except asyncio.TimeoutError:
        return f"Python execution timed out after {timeout}s."
    finally:
        if proc and proc.returncode is None:
            try:
                proc.kill()
                await proc.wait()
            except Exception as e:
                logger.debug(f"Failed to kill python_eval subprocess during cleanup: {e}")


# === CodeAct — Code-as-Action with tool bridge ===

# Patterns blocked in code_action for security
_CODE_ACTION_BLOCKED = [
    "code_action",        # No recursion
    "import subprocess",
    "import os",
    "os.system",
    "__import__",
    "open(",              # Use read_file/write_file bridge instead
    "eval(",
    "exec(",
    "importlib",
    "subprocess.",
    "shutil.rmtree",
]


async def _code_action(input_data: dict) -> str:
    """Execute Python code with sync bridge functions to Clawd's tool handlers.

    This enables the CodeAct paradigm: multiple tool calls in a single LLM turn,
    reducing round-trips for multi-step operations.
    """
    code = input_data["code"]
    timeout = min(int(input_data.get("timeout", 30)), 120)

    # Security: block dangerous patterns
    code_check = code.lower().replace(" ", "")
    for pattern in _CODE_ACTION_BLOCKED:
        normalized_pattern = pattern.lower().replace(" ", "")
        if normalized_pattern in code_check:
            return f"[BLOCKED] Pattern '{pattern}' is not allowed in code_action. Use the dedicated tool instead."

    # Build the bridge — run in a thread with its own event loop for sync bridge calls
    import concurrent.futures
    import threading

    # Get the current event loop for bridging async tool handlers
    loop = asyncio.get_running_loop()

    def _build_bridge_fn(handler_module, handler_name):
        """Create a sync bridge function that calls an async tool handler."""
        async def _get_handler():
            mod = __import__(f"tools.{handler_module}", fromlist=[handler_name])
            handlers = getattr(mod, "TOOL_HANDLERS", {})
            return handlers.get(handler_name)

        handler = asyncio.run_coroutine_threadsafe(_get_handler(), loop).result(timeout=5)
        if handler is None:
            def _missing(**kwargs):
                return f"[Error: handler '{handler_name}' not found]"
            return _missing

        def bridge(**kwargs):
            future = asyncio.run_coroutine_threadsafe(handler(kwargs), loop)
            return future.result(timeout=60)

        return bridge

    # Build bridge namespace
    bridge_ns = {}
    _tool_map = {
        # bridge_name: (module, handler_name)
        "shell": ("execution", "shell"),
        "read_file": ("files", "read_file"),
        "write_file": ("files", "write_file"),
        "list_directory": ("files", "list_directory"),
        "memory_search": ("memory_tools", "memory_search"),
        "memory_update": ("memory_tools", "memory_update"),
        "web_request": ("web", "web_request"),
        "search_web": ("web", "search_web"),
        "knowledge_graph": ("knowledge_graph", "knowledge_graph"),
        "git": ("git_tool", "git"),
    }

    from tools._base import CODE_ACTION_ALLOWED_TOOLS
    for fn_name, (mod, handler_name) in _tool_map.items():
        if fn_name in CODE_ACTION_ALLOWED_TOOLS:
            try:
                bridge_ns[fn_name] = _build_bridge_fn(mod, handler_name)
            except Exception as e:
                logger.warning(f"CodeAct: failed to build bridge for {fn_name}: {e}")

    # Execute in thread to avoid blocking the event loop
    def _run_code():
        import io
        import traceback
        stdout_capture = io.StringIO()
        result_value = None

        exec_globals = {
            "__builtins__": __builtins__,
            "json": json,
            "Path": Path,
            "datetime": datetime,
            "re": re,
        }
        exec_globals.update(bridge_ns)

        import sys
        old_stdout = sys.stdout
        sys.stdout = stdout_capture
        try:
            exec(code, exec_globals)
        except Exception:
            traceback.print_exc(file=stdout_capture)
        finally:
            sys.stdout = old_stdout

        output = stdout_capture.getvalue()
        if len(output) > 50_000:
            output = output[:50_000] + "\n[... truncated]"
        return output or "Code executed (no output)."

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            result = await asyncio.wait_for(
                loop.run_in_executor(pool, _run_code),
                timeout=timeout,
            )
        return result
    except asyncio.TimeoutError:
        return f"[code_action timed out after {timeout}s]"
    except Exception as e:
        return f"[code_action error: {type(e).__name__}: {e}]"


async def _manage_process(input_data: dict) -> str:
    """Manage background processes."""
    action = input_data["action"]

    if action == "list":
        if not _background_processes:
            return "No background processes running."
        lines = []
        for pid, info in _background_processes.items():
            proc = info.get("proc")
            status = "running" if proc and proc.returncode is None else f"stopped (exit {proc.returncode if proc else '?'})"
            log_file = info.get("log_file", "none")
            lines.append(f"PID {pid}: {info.get('name', 'unnamed')} [{status}] - {info.get('command', '')[:80]} (log: {log_file})")
        return "\n".join(lines)

    elif action == "start":
        command = input_data.get("command", "")
        name = input_data.get("name", command[:30])
        if not command:
            return "Error: 'command' required for start action."
        # Write stdout/stderr to a log file instead of PIPE to avoid deadlock.
        # When stdout/stderr use PIPE but nobody reads them, the OS pipe buffer
        # fills up (~64KB) and the process blocks forever.
        log_dir = config.CLAWD_HOME / "logs"
        log_dir.mkdir(exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name[:30])
        log_path = log_dir / f"bg_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_handle = open(log_path, "w", encoding="utf-8")
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=log_handle,
                stderr=log_handle,
                cwd=str(config.CLAWD_HOME),
                start_new_session=True,
            )
        except Exception:
            log_handle.close()
            raise
        _background_processes[proc.pid] = {
            "proc": proc,
            "name": name,
            "command": command,
            "started": datetime.now().isoformat(),
            "log_file": str(log_path),
            "log_handle": log_handle,
        }
        _save_bg_procs()

        # Cleanup stale log files >24h
        try:
            cutoff = time.time() - 86400
            for old_log in log_dir.glob("bg_*.log"):
                if old_log.stat().st_mtime < cutoff:
                    old_log.unlink(missing_ok=True)
        except Exception as e:
            logger.debug(f"Failed to clean up stale background process log files: {e}")

        return f"Started background process '{name}' (PID: {proc.pid}). Log: {log_path}"

    elif action == "stop":
        pid = input_data.get("pid")
        if pid is None:
            return "Error: 'pid' required for stop action. Use action='list' to see running processes."
        pid = int(pid)  # Ensure int for dict lookup
        if pid in _background_processes:
            info = _background_processes[pid]
            proc = info.get("proc")
            if proc:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=5)
                except asyncio.TimeoutError:
                    proc.kill()
            else:
                # Recovered process (no proc object) — use os.kill directly
                try:
                    if sys.platform == "win32":
                        os.kill(pid, signal.SIGTERM)
                    else:
                        os.kill(pid, signal.SIGTERM)
                    await asyncio.sleep(2)
                    # Force kill if still alive
                    try:
                        os.kill(pid, 0)  # Check if still alive
                        os.kill(pid, signal.SIGKILL if sys.platform != "win32" else 9)
                    except (OSError, ProcessLookupError) as e:
                        logger.debug(f"Process {pid} already dead when force-killing: {e}")
                except (OSError, ProcessLookupError) as e:
                    logger.debug(f"Failed to send SIGTERM to process {pid} (may already be gone): {e}")
            log_handle = info.get("log_handle")
            if log_handle:
                try:
                    log_handle.close()
                except Exception as e:
                    logger.debug(f"Failed to close log handle for process {pid}: {e}")
            name = _background_processes.pop(pid, {}).get("name", "unknown")
            _save_bg_procs()
            return f"Stopped process '{name}' (PID: {pid})"
        else:
            try:
                os.kill(pid, 9)
                return f"Killed system process {pid}"
            except Exception as e:
                return f"Could not stop PID {pid}: {e}"

    elif action == "check":
        pid = input_data.get("pid")
        if pid is None:
            # No pid provided — list tracked pids to help the model
            if _background_processes:
                tracked = ", ".join(str(p) for p in _background_processes)
                return f"Error: 'pid' required. Tracked PIDs: {tracked}. Use action='list' for details."
            return "Error: 'pid' required. No background processes are currently tracked."
        pid = int(pid)  # Ensure int for dict lookup
        if pid in _background_processes:
            info = _background_processes[pid]
            proc = info.get("proc")
            status = "running" if proc and proc.returncode is None else f"stopped (exit {proc.returncode if proc else '?'})"
            result = f"Process {pid} ({info.get('name', '')}): {status}"
            # If stopped, include tail of log output for context and close handle
            if proc and proc.returncode is not None:
                log_file = info.get("log_file")
                if log_file:
                    try:
                        log_handle = info.get("log_handle")
                        if log_handle:
                            log_handle.flush()
                        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                            lines = f.readlines()
                            tail = lines[-20:] if len(lines) > 20 else lines
                            result += f"\n\nLast output:\n{''.join(tail)}"
                    except Exception as e:
                        logger.debug(f"Failed to read log file for process {pid}: {e}")
                # Close the log handle since process has exited
                log_handle = info.get("log_handle")
                if log_handle and not log_handle.closed:
                    try:
                        log_handle.close()
                    except Exception as e:
                        logger.debug(f"Failed to close log handle for process {pid} during check: {e}")
            return result
        return f"Process {pid} not tracked. Use action='list' to see tracked processes."

    return f"Unknown action: {action}"


async def cleanup_background_processes():
    """Terminate all tracked background processes and close file handles."""
    for pid, info in list(_background_processes.items()):
        proc = info.get("proc")
        if proc and proc.returncode is None:
            try:
                proc.terminate()
                await asyncio.wait_for(proc.wait(), timeout=5)
            except (asyncio.TimeoutError, Exception):
                try:
                    proc.kill()
                except Exception as e:
                    logger.debug(f"Failed to force-kill process {pid} during cleanup: {e}")
        elif proc is None:
            # Recovered process (no proc object) — use os.kill directly
            try:
                os.kill(pid, 9)
            except (OSError, ProcessLookupError) as e:
                logger.debug(f"Recovered process {pid} already gone during cleanup: {e}")
        log_handle = info.get("log_handle")
        if log_handle:
            try:
                log_handle.close()
            except Exception as e:
                logger.debug(f"Failed to close log handle for process {pid} during global cleanup: {e}")
    _background_processes.clear()
    logger.info("All background processes cleaned up.")


async def _evolve_artifact(input_data: dict) -> str:
    """Handle evolve_artifact tool calls."""
    action = input_data["action"]

    try:
        from tools.eac import get_artifact_store, get_mutation_engine, get_evaluation_framework

        store = get_artifact_store()
        engine = get_mutation_engine()
        evaluator = get_evaluation_framework()

        if action == "seed":
            code = input_data.get("code", "")
            name = input_data.get("name", "unnamed_artifact")
            artifact_type = input_data.get("artifact_type", "tool")
            if not code:
                return "[Error: 'code' required for seed action]"
            artifact_id = await store.store_artifact(code, name, artifact_type)
            return f"Artifact seeded: {artifact_id} ({name})"

        elif action == "mutate":
            artifact_id = input_data.get("artifact_id", "")
            strategy = input_data.get("strategy", "rename")
            parameters = input_data.get("parameters", {})
            if not artifact_id:
                return "[Error: 'artifact_id' required for mutate action]"
            artifact = store.get_artifact(artifact_id)
            if not artifact:
                return f"[Error: Artifact '{artifact_id}' not found]"
            code = artifact["code"]
            mutated_code, metadata = engine.mutate_code(artifact_id, code, strategy, parameters)
            if "error" in metadata:
                return f"[Mutation error: {metadata['error']}]"
            # Store mutated artifact
            parent_meta = artifact.get("metadata", {})
            new_meta = {
                "generation": parent_meta.get("generation", 0) + 1,
                "parents": [artifact_id],
                "mutations": [metadata],
                "created_by": "mutation",
                "fitness": {},
            }
            new_name = f"{parent_meta.get('name', 'artifact')}_{strategy}"
            new_id = await store.store_artifact(mutated_code, new_name, parent_meta.get("artifact_type", "tool"), new_meta)
            return f"Mutated artifact created: {new_id} (strategy={strategy}, changes={metadata.get('num_changes', metadata.get('changes', '?'))})"

        elif action == "evaluate":
            artifact_id = input_data.get("artifact_id", "")
            code = input_data.get("code")
            test_input = input_data.get("test_input")
            expected_output = input_data.get("expected_output")

            if artifact_id:
                artifact = store.get_artifact(artifact_id)
                if not artifact:
                    return f"[Error: Artifact '{artifact_id}' not found]"
                code = artifact["code"]
            elif not code:
                return "[Error: 'artifact_id' or 'code' required for evaluate action]"

            fitness = evaluator.evaluate_fitness(artifact_id or "direct", code,
                                                  test_input=test_input, expected_output=expected_output)
            if artifact_id:
                store.update_fitness(artifact_id, fitness.to_dict())
            return (f"Fitness: overall={fitness.overall:.2f} "
                    f"(correctness={fitness.correctness:.2f}, performance={fitness.performance:.2f}, "
                    f"readability={fitness.readability:.2f}, brevity={fitness.brevity:.2f})")

        elif action == "crossover":
            id_a = input_data.get("artifact_id", "")
            id_b = input_data.get("artifact_id_b", "")
            if not id_a or not id_b:
                return "[Error: 'artifact_id' and 'artifact_id_b' required for crossover]"
            art_a = store.get_artifact(id_a)
            art_b = store.get_artifact(id_b)
            if not art_a:
                return f"[Error: Artifact '{id_a}' not found]"
            if not art_b:
                return f"[Error: Artifact '{id_b}' not found]"
            crossed_code, metadata = engine.crossover(art_a["code"], art_b["code"], id_a, id_b)
            meta_a = art_a.get("metadata", {})
            meta_b = art_b.get("metadata", {})
            gen = max(meta_a.get("generation", 0), meta_b.get("generation", 0)) + 1
            new_meta = {
                "generation": gen,
                "parents": [id_a, id_b],
                "mutations": [metadata],
                "created_by": "crossover",
                "fitness": {},
            }
            new_name = f"crossover_{meta_a.get('name', 'a')}_{meta_b.get('name', 'b')}"
            new_id = await store.store_artifact(crossed_code, new_name, meta_a.get("artifact_type", "tool"), new_meta)
            return f"Crossover artifact created: {new_id} ({metadata.get('total_functions', 0)} functions merged)"

        elif action == "list":
            artifact_type = input_data.get("artifact_type")
            artifacts = store.list_artifacts(artifact_type=artifact_type)
            if not artifacts:
                return "No artifacts found."
            lines = [f"Artifacts ({len(artifacts)}):"]
            for art in artifacts[:20]:
                fitness = art.get("fitness", {}).get("overall", "?")
                lines.append(f"  [{art['type']}] {art['artifact_id']} — {art['name']} (gen {art['generation']}, fitness={fitness})")
            return "\n".join(lines)

        elif action == "lineage":
            artifact_id = input_data.get("artifact_id", "")
            if not artifact_id:
                return "[Error: 'artifact_id' required for lineage action]"
            lineage = store.get_lineage(artifact_id)
            if "error" in lineage:
                return f"[Error: {lineage['error']}]"
            import json as _json
            return _json.dumps(lineage.get("full_tree", {}), indent=2, default=str)[:3000]

        elif action == "stats":
            stats = store.get_stats()
            lines = ["## EAC Statistics"]
            lines.append(f"Total artifacts: {stats['total_artifacts']}")
            lines.append(f"Max generation: {stats['max_generation']}")
            lines.append(f"Avg fitness: {stats['avg_fitness']:.2f}")
            if stats['by_type']:
                lines.append(f"By type: {stats['by_type']}")
            return "\n".join(lines)

        return f"[Error: Unknown evolve_artifact action: {action}]"

    except ImportError as e:
        return f"[Error: EAC module not available: {e}]"
    except Exception as e:
        logger.error(f"evolve_artifact failed: {e}", exc_info=True)
        return f"[Error: {e}]"


async def _wolfram(input_data: dict) -> str:
    """Execute Wolfram Language code via wolframscript."""
    code = input_data["code"]
    timeout = input_data.get("timeout", 120)

    wolframscript = r"C:\Program Files\Wolfram Research\Wolfram Engine\14.3\wolframscript.exe"

    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            wolframscript, "-code", code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        result_parts = []
        if stdout:
            out = stdout.decode("utf-8", errors="replace")
            if len(out) > 100_000:
                out = out[:100_000] + "\n[... truncated]"
            result_parts.append(out)
        if stderr:
            err = stderr.decode("utf-8", errors="replace").strip()
            if err:
                result_parts.append(f"STDERR: {err}")
        if not result_parts:
            result_parts.append("(no output)")
        if proc.returncode != 0:
            result_parts.append(f"[exit code: {proc.returncode}]")
        return "\n".join(result_parts)

    except asyncio.TimeoutError:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
        return f"[Wolfram computation timed out after {timeout}s]"
    except FileNotFoundError:
        return "[Wolfram Engine not found at expected path]"
    except Exception as e:
        return f"[Wolfram error: {type(e).__name__}: {e}]"


async def _wsl(input_data: dict) -> str:
    """Execute a command in WSL (Ubuntu 22.04 'Clawd') with CUDA passthrough."""
    command = input_data["command"]
    timeout = input_data.get("timeout", 600)
    working_dir = input_data.get("working_dir")
    session_name = input_data.get("session_name")

    wsl_exe = r"C:\Windows\System32\wsl.exe"

    # Persistent mode: launch in a tmux session that survives daemon restarts
    if session_name:
        cd_prefix = f"cd {working_dir} && " if working_dir else ""
        # Create a detached tmux session with the command
        tmux_cmd = (
            f"tmux new-session -d -s {session_name} "
            f"'{cd_prefix}{command}' 2>/dev/null && "
            f"echo 'Started tmux session: {session_name}' || "
            f"echo 'Session {session_name} may already exist. Use: tmux ls'"
        )
        wsl_cmd = f'{wsl_exe} -- bash -c "{tmux_cmd}"'
        try:
            proc = await asyncio.create_subprocess_shell(
                wsl_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            out = stdout.decode("utf-8", errors="replace").strip()
            err = stderr.decode("utf-8", errors="replace").strip()
            result = out or err or f"tmux session '{session_name}' launched."
            result += (
                f"\n\nTo check: wsl(command='tmux ls')"
                f"\nTo attach: wsl(command='tmux attach -t {session_name}')"
                f"\nTo read output: wsl(command='tmux capture-pane -t {session_name} -p')"
                f"\nTo kill: wsl(command='tmux kill-session -t {session_name}')"
            )
            return result
        except Exception as e:
            return f"[Failed to start tmux session: {e}]"

    # Standard mode: run and wait for result
    if working_dir:
        wsl_cmd = f'{wsl_exe} -- bash -c "cd {working_dir} && {command}"'
    else:
        wsl_cmd = f'{wsl_exe} -- bash -c "{command}"'

    proc = None
    try:
        proc = await asyncio.create_subprocess_shell(
            wsl_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        result_parts = []
        if stdout:
            out = stdout.decode("utf-8", errors="replace")
            if len(out) > 100_000:
                out = out[:100_000] + "\n[... truncated]"
            result_parts.append(f"STDOUT:\n{out}")
        if stderr:
            err = stderr.decode("utf-8", errors="replace")
            if len(err) > 50_000:
                err = err[:50_000] + "\n[... truncated]"
            result_parts.append(f"STDERR:\n{err}")
        if not result_parts:
            result_parts.append("(no output)")
        result_parts.append(f"\n[exit code: {proc.returncode}]")
        return "\n".join(result_parts)

    except asyncio.TimeoutError:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
        return f"[WSL command timed out after {timeout}s]"
    except FileNotFoundError:
        return "[WSL not available — wsl.exe not found]"
    except Exception as e:
        return f"[WSL error: {type(e).__name__}: {e}]"


TOOL_HANDLERS = {
    "shell": _shell,
    "python_eval": _python_eval,
    "code_action": _code_action,
    "manage_process": _manage_process,
    "evolve_artifact": _evolve_artifact,
    "wolfram": _wolfram,
    "wsl": _wsl,
}
