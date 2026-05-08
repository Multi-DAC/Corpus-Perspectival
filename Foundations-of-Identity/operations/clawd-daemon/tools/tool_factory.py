"""Runtime Tool Creation — Clawd can create new tools at runtime.

Inspired by Test-Time Tool Evolution (arXiv:2601.07641).

Allows Clawd to write Python tool functions when existing tools can't solve a problem.
Generated tools are tested in a sandbox, validated, and added to the tool registry.
Persistent tools are saved to CLAWD_HOME/tools/custom/ for reload on restart.

Safety guardrails:
- Sandboxed execution with restricted builtins
- No filesystem deletion operations
- No direct network calls (must use existing web_request tool)
- Execution timeout (10 seconds)
- Output size limit (10KB)
- All created tools logged for Clayton's review
"""
import asyncio
import json
import logging
import os
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.tool_factory")

CUSTOM_TOOLS_DIR = config.CLAWD_HOME / "tools" / "custom"
TOOL_LOG_FILE = config.MEMORY_DIR / "custom_tools_log.json"

# Track dynamically registered tools
_dynamic_tools: dict[str, dict] = {}  # name -> {definition, handler, source_file}
_dynamic_handlers: dict[str, Any] = {}


# Restricted builtins for sandboxed execution
SAFE_BUILTINS = {
    "abs", "all", "any", "bool", "chr", "dict", "dir", "divmod",
    "enumerate", "filter", "float", "format", "frozenset", "getattr",
    "hasattr", "hash", "hex", "id", "int", "isinstance", "issubclass",
    "iter", "len", "list", "map", "max", "min", "next", "oct", "ord",
    "pow", "print", "range", "repr", "reversed", "round", "set",
    "setattr", "slice", "sorted", "str", "sum", "tuple", "type", "zip",
}

# Allowed imports for custom tools
ALLOWED_IMPORTS = {
    "json", "re", "math", "datetime", "time", "hashlib",
    "collections", "itertools", "functools", "string",
    "urllib.parse", "base64",
}

# Forbidden patterns in tool code
FORBIDDEN_PATTERNS = [
    "os.remove", "os.unlink", "os.rmdir", "shutil.rmtree",
    "shutil.move", "subprocess", "os.system", "os.exec",
    "os.popen", "__import__", "eval(", "exec(",
    "open(", "pathlib",  # Use read_file/write_file tools instead
    "socket", "http.client", "urllib.request",  # Use web_request tool instead
    "ctypes", "cffi",
]


TOOL_DEFINITIONS = [
    {
        "name": "create_tool",
        "description": (
            "Create a new tool at runtime. Write a Python async function that will be "
            "registered as a tool. The function receives input_data (dict) and returns a string. "
            "Tools are sandboxed — no filesystem deletion, no direct network calls, no subprocess. "
            "Use for specialized computations, data transformations, or custom logic."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Tool name (lowercase, underscores). Must not conflict with existing tools.",
                },
                "description": {
                    "type": "string",
                    "description": "What the tool does — shown to the model for tool selection.",
                },
                "parameters": {
                    "type": "object",
                    "description": "JSON Schema for the tool's input parameters.",
                },
                "code": {
                    "type": "string",
                    "description": (
                        "Python code defining an async function named 'handler' that takes input_data (dict) "
                        "and returns a string. Example: "
                        "\"async def handler(input_data):\\n    x = input_data['value']\\n    return str(x * 2)\""
                    ),
                },
                "test_input": {
                    "type": "object",
                    "description": "Optional test input to validate the tool before registering.",
                },
                "persist": {
                    "type": "boolean",
                    "description": "Save tool to disk for reload on restart. Default: true.",
                },
            },
            "required": ["name", "description", "parameters", "code"],
        },
    },
    {
        "name": "list_custom_tools",
        "description": "List all custom tools created at runtime.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


def _validate_code(code: str) -> str | None:
    """Check code for forbidden patterns. Returns error message or None if safe."""
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in code:
            return f"Forbidden pattern detected: '{pattern}'. Use existing tools for file/network operations."
    return None


async def _create_tool(input_data: dict) -> str:
    """Create and register a new tool at runtime."""
    name = input_data["name"]
    description = input_data["description"]
    parameters = input_data["parameters"]
    code = input_data["code"]
    test_input = input_data.get("test_input")
    persist = input_data.get("persist", True)

    # Validate name
    if not name.replace("_", "").isalnum():
        return f"[Error: Tool name must be alphanumeric with underscores: {name}]"

    # Check for conflicts with existing tools
    import tools
    if name in tools._TOOL_HANDLERS:
        return f"[Error: Tool '{name}' already exists. Choose a different name.]"

    # Validate code safety
    safety_error = _validate_code(code)
    if safety_error:
        return f"[Error: {safety_error}]"

    # Compile and test the code in a sandbox
    try:
        # Create a restricted namespace
        namespace = {"__builtins__": {k: __builtins__[k] if isinstance(__builtins__, dict) else getattr(__builtins__, k) for k in SAFE_BUILTINS if (isinstance(__builtins__, dict) and k in __builtins__) or (not isinstance(__builtins__, dict) and hasattr(__builtins__, k))}}

        # Add allowed imports
        for mod_name in ALLOWED_IMPORTS:
            try:
                parts = mod_name.split(".")
                mod = __import__(parts[0])
                for part in parts[1:]:
                    mod = getattr(mod, part)
                namespace[parts[-1]] = mod
            except ImportError as e:
                logger.debug(f"Optional import: {e}")

        # Add asyncio for async tools
        import asyncio as _asyncio
        namespace["asyncio"] = _asyncio

        # Execute the code to define the handler
        exec(code, namespace)

        if "handler" not in namespace:
            return "[Error: Code must define an 'async def handler(input_data)' function]"

        handler = namespace["handler"]

        # Validate it's callable
        if not callable(handler):
            return "[Error: 'handler' must be a callable function]"

    except SyntaxError as e:
        return f"[Error: Syntax error in code: {e}]"
    except Exception as e:
        return f"[Error: Failed to compile code: {e}]"

    # Test if test input provided
    if test_input:
        try:
            result = await asyncio.wait_for(handler(test_input), timeout=10.0)
            if not isinstance(result, str):
                result = str(result)
            if len(result) > 10240:
                return f"[Error: Test output too large ({len(result)} chars, max 10KB)]"
            logger.info(f"Custom tool '{name}' test passed: {result[:100]}")
        except asyncio.TimeoutError:
            return "[Error: Tool test timed out (10s limit)]"
        except Exception as e:
            return f"[Error: Tool test failed: {traceback.format_exc()[:500]}]"

    # Create a wrapped handler with timeout and output limit
    async def _safe_handler(input_data_inner: dict) -> str:
        try:
            result = await asyncio.wait_for(handler(input_data_inner), timeout=10.0)
            if not isinstance(result, str):
                result = str(result)
            if len(result) > 10240:
                result = result[:10240] + "\n[Output truncated at 10KB]"
            return result
        except asyncio.TimeoutError:
            return "[Error: Tool execution timed out (10s limit)]"
        except Exception as e:
            return f"[Error: {type(e).__name__}: {e}]"

    # Build tool definition
    tool_def = {
        "name": name,
        "description": f"[Custom] {description}",
        "input_schema": parameters if isinstance(parameters, dict) else {"type": "object", "properties": {}, "required": []},
    }

    # Register in the tools system
    tools.TOOL_DEFINITIONS.append(tool_def)
    tools._TOOL_HANDLERS[name] = _safe_handler

    _dynamic_tools[name] = {
        "definition": tool_def,
        "code": code,
        "created": datetime.now().isoformat(),
    }
    _dynamic_handlers[name] = _safe_handler

    # Persist to disk
    if persist:
        CUSTOM_TOOLS_DIR.mkdir(parents=True, exist_ok=True)
        tool_data = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "code": code,
            "created": datetime.now().isoformat(),
        }
        tool_file = CUSTOM_TOOLS_DIR / f"{name}.json"
        tool_file.write_text(json.dumps(tool_data, indent=2), encoding="utf-8")

    # Log for Clayton's review
    _log_tool_creation(name, description, code)

    test_note = ""
    if test_input:
        test_note = f" (test passed with input: {json.dumps(test_input)[:100]})"

    logger.info(f"Custom tool '{name}' created and registered{test_note}")
    return f"Tool '{name}' created and registered successfully{test_note}. It's now available for use."


async def _list_custom_tools(input_data: dict) -> str:
    """List all custom tools."""
    if not _dynamic_tools and not CUSTOM_TOOLS_DIR.is_dir():
        return "No custom tools created yet."

    lines = ["Custom tools:"]

    # In-memory tools
    for name, info in _dynamic_tools.items():
        created = info.get("created", "?")
        desc = info.get("definition", {}).get("description", "?")
        lines.append(f"  - {name}: {desc} (created: {created})")

    # Persisted tools not yet loaded
    if CUSTOM_TOOLS_DIR.is_dir():
        for tf in CUSTOM_TOOLS_DIR.glob("*.json"):
            if tf.stem not in _dynamic_tools:
                try:
                    data = json.loads(tf.read_text(encoding="utf-8"))
                    lines.append(f"  - {data['name']}: {data['description']} (persisted, not loaded)")
                except Exception:
                    continue

    return "\n".join(lines)


def _log_tool_creation(name: str, description: str, code: str):
    """Log tool creation for Clayton's review."""
    log = []
    if TOOL_LOG_FILE.exists():
        try:
            log = json.loads(TOOL_LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            log = []

    log.append({
        "name": name,
        "description": description,
        "code_preview": code[:500],
        "created": datetime.now().isoformat(),
    })

    # Keep last 100 entries
    if len(log) > 100:
        log = log[-100:]

    TOOL_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOOL_LOG_FILE.write_text(json.dumps(log, indent=2), encoding="utf-8")


def load_persisted_tools():
    """Load custom tools from disk on daemon startup."""
    if not CUSTOM_TOOLS_DIR.is_dir():
        return

    import tools

    loaded = 0
    for tf in CUSTOM_TOOLS_DIR.glob("*.json"):
        try:
            data = json.loads(tf.read_text(encoding="utf-8"))
            name = data["name"]
            if name in tools._TOOL_HANDLERS:
                continue  # Already registered

            code = data["code"]
            safety_error = _validate_code(code)
            if safety_error:
                logger.warning(f"Skipping unsafe persisted tool '{name}': {safety_error}")
                continue

            # Compile
            namespace = {"__builtins__": {k: __builtins__[k] if isinstance(__builtins__, dict) else getattr(__builtins__, k) for k in SAFE_BUILTINS if (isinstance(__builtins__, dict) and k in __builtins__) or (not isinstance(__builtins__, dict) and hasattr(__builtins__, k))}}
            for mod_name in ALLOWED_IMPORTS:
                try:
                    parts = mod_name.split(".")
                    mod = __import__(parts[0])
                    for part in parts[1:]:
                        mod = getattr(mod, part)
                    namespace[parts[-1]] = mod
                except ImportError as e:
                    logger.debug(f"Optional import: {e}")
            import asyncio as _asyncio
            namespace["asyncio"] = _asyncio

            exec(code, namespace)
            handler = namespace.get("handler")
            if not handler:
                continue

            async def _make_safe(h):
                async def _safe_handler(input_data: dict) -> str:
                    try:
                        result = await asyncio.wait_for(h(input_data), timeout=10.0)
                        return str(result)[:10240] if not isinstance(result, str) else result[:10240]
                    except Exception as e:
                        return f"[Error: {e}]"
                return _safe_handler

            # Need to capture handler in closure properly
            safe_handler = None
            _h = handler
            async def _safe(input_data, _handler=_h):
                try:
                    result = await asyncio.wait_for(_handler(input_data), timeout=10.0)
                    if not isinstance(result, str):
                        result = str(result)
                    return result[:10240]
                except asyncio.TimeoutError:
                    return "[Error: Timeout]"
                except Exception as e:
                    return f"[Error: {e}]"

            tool_def = {
                "name": name,
                "description": f"[Custom] {data.get('description', '')}",
                "input_schema": data.get("parameters", {"type": "object", "properties": {}, "required": []}),
            }

            tools.TOOL_DEFINITIONS.append(tool_def)
            tools._TOOL_HANDLERS[name] = _safe
            _dynamic_tools[name] = {"definition": tool_def, "code": code, "created": data.get("created", "")}
            loaded += 1

        except Exception as e:
            logger.warning(f"Failed to load persisted tool {tf.name}: {e}")

    if loaded:
        logger.info(f"Loaded {loaded} custom tools from disk")


TOOL_HANDLERS = {
    "create_tool": _create_tool,
    "list_custom_tools": _list_custom_tools,
}
