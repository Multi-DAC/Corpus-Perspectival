"""
Base utilities and MCP-compatible tool metadata shared across all tool modules.
"""
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("clawd.tools.base")

# Sensitive paths that should be logged when accessed
_SENSITIVE_PATH_PREFIXES = ("/etc/", "/var/", "/root/", "C:\\Windows\\", "C:\\Program Files")


def resolve_path(path_str: str) -> Path:
    """Resolve a path — absolute stays absolute, relative resolves from CLAWD_HOME.
    Normalizes with .resolve() and logs access to sensitive/external paths."""
    p = Path(path_str)
    if p.is_absolute():
        resolved = p.resolve()
    else:
        resolved = (config.CLAWD_HOME / p).resolve()

    # Audit log: warn on paths outside CLAWD_HOME or in sensitive locations
    try:
        resolved.relative_to(config.CLAWD_HOME.resolve())
    except ValueError:
        # Path is outside CLAWD_HOME — log for audit
        path_s = str(resolved)
        if any(path_s.startswith(prefix) for prefix in _SENSITIVE_PATH_PREFIXES):
            logger.warning(f"PATH AUDIT: Accessing sensitive path outside CLAWD_HOME: {resolved}")
        else:
            logger.info(f"PATH AUDIT: Accessing path outside CLAWD_HOME: {resolved}")

    return resolved


# === MCP-Compatible Tool Metadata ===

@dataclass
class ToolMetadata:
    """MCP-compatible metadata for tool definitions."""
    version: str = "1.0.0"
    author: str = "Clawd"
    category: str = "general"
    safety_level: str = "safe"  # safe, caution, dangerous, critical
    requires_confirmation: bool = False
    side_effects: list = field(default_factory=list)  # filesystem, network, process, memory
    rate_limit: Optional[int] = None  # max calls per minute, None = unlimited
    timeout: Optional[int] = None  # default timeout in seconds
    deprecated: bool = False


# Safety registry: tool name -> metadata
TOOL_SAFETY_REGISTRY: dict[str, ToolMetadata] = {
    # Execution tools — dangerous
    "shell": ToolMetadata(category="execution", safety_level="dangerous",
                          requires_confirmation=False, side_effects=["filesystem", "process", "network"],
                          timeout=600),
    "python_eval": ToolMetadata(category="execution", safety_level="caution",
                                side_effects=["filesystem", "process"], timeout=300),
    "code_action": ToolMetadata(category="execution", safety_level="dangerous",
                                requires_confirmation=False,
                                side_effects=["filesystem", "process", "network", "memory"],
                                timeout=120),
    "manage_process": ToolMetadata(category="execution", safety_level="caution",
                                   side_effects=["process"]),

    # File tools — caution
    "read_file": ToolMetadata(category="files", safety_level="safe", side_effects=[]),
    "write_file": ToolMetadata(category="files", safety_level="caution",
                               side_effects=["filesystem"]),
    "list_directory": ToolMetadata(category="files", safety_level="safe", side_effects=[]),

    # Memory tools — safe (internal persistence)
    "memory_search": ToolMetadata(category="memory", safety_level="safe", side_effects=[]),
    "memory_update": ToolMetadata(category="memory", safety_level="safe",
                                  side_effects=["memory"]),
    "memory_extract": ToolMetadata(category="memory", safety_level="safe",
                                   side_effects=["memory"]),
    "memory_items": ToolMetadata(category="memory", safety_level="safe",
                                 side_effects=["memory"]),
    "memory_categories": ToolMetadata(category="memory", safety_level="safe",
                                      side_effects=["memory"]),
    "working_memory": ToolMetadata(category="memory", safety_level="safe",
                                   side_effects=["memory"]),

    # Knowledge & Intelligence
    "knowledge_graph": ToolMetadata(category="knowledge", safety_level="safe",
                                    side_effects=["memory"]),
    "reflect": ToolMetadata(category="intelligence", safety_level="safe",
                            side_effects=["memory"]),
    "goals": ToolMetadata(category="intelligence", safety_level="safe",
                          side_effects=["memory"]),
    "experience": ToolMetadata(category="intelligence", safety_level="safe",
                               side_effects=["memory"]),
    "verify_action": ToolMetadata(category="intelligence", safety_level="safe",
                                  side_effects=[]),
    "self_improve": ToolMetadata(category="intelligence", safety_level="safe",
                                 side_effects=["memory"]),
    "consolidate_memory": ToolMetadata(category="intelligence", safety_level="safe",
                                       side_effects=["memory"]),

    # Communication — caution (external effects)
    "send_telegram": ToolMetadata(category="communication", safety_level="caution",
                                  requires_confirmation=False, side_effects=["network"]),
    "speak": ToolMetadata(category="communication", safety_level="safe",
                          side_effects=["process"]),

    # Web tools — caution
    "web_request": ToolMetadata(category="web", safety_level="caution",
                                side_effects=["network"]),
    "search_web": ToolMetadata(category="web", safety_level="safe",
                               side_effects=["network"]),
    "deep_research": ToolMetadata(category="web", safety_level="safe",
                                  side_effects=["network"]),
    "browser": ToolMetadata(category="web", safety_level="caution",
                            side_effects=["network", "process"]),

    # System tools
    "get_current_time": ToolMetadata(category="system", safety_level="safe",
                                     side_effects=[]),
    "switch_model": ToolMetadata(category="system", safety_level="safe",
                                 side_effects=[]),
    "system_status": ToolMetadata(category="system", safety_level="safe",
                                  side_effects=[]),
    "consult": ToolMetadata(category="system", safety_level="safe",
                            side_effects=["network"], timeout=120),
    "parallel_consult": ToolMetadata(category="system", safety_level="safe",
                                     side_effects=["network"], timeout=300),
    "collaborative_consult": ToolMetadata(category="system", safety_level="safe",
                                          side_effects=["network"], timeout=600),
    "plan_and_execute": ToolMetadata(category="system", safety_level="caution",
                                     side_effects=["network", "memory"], timeout=600),
    "resume_plan": ToolMetadata(category="system", safety_level="caution",
                                side_effects=["network", "memory"]),
    "run_skill": ToolMetadata(category="system", safety_level="caution",
                              side_effects=["filesystem", "network"]),

    # Meta tools
    "meta_agent": ToolMetadata(category="meta", safety_level="safe",
                               side_effects=["memory"]),
    "dashboard": ToolMetadata(category="meta", safety_level="safe",
                              side_effects=[]),

    # Other
    "git": ToolMetadata(category="git", safety_level="caution",
                        side_effects=["filesystem", "network"]),
    "schedule": ToolMetadata(category="scheduling", safety_level="safe",
                             side_effects=["memory"]),
    "screenshot": ToolMetadata(category="screen", safety_level="safe",
                               side_effects=[]),
    "clipboard": ToolMetadata(category="screen", safety_level="safe",
                              side_effects=[]),
    "vision": ToolMetadata(category="vision", safety_level="safe",
                           side_effects=["network"]),
    "market_data": ToolMetadata(category="financial", safety_level="safe",
                                side_effects=["network"]),
    "create_tool": ToolMetadata(category="meta", safety_level="caution",
                                side_effects=["filesystem"]),
    "list_custom_tools": ToolMetadata(category="meta", safety_level="safe",
                                      side_effects=[]),

    # Desktop embodiment
    "desktop": ToolMetadata(category="screen", safety_level="caution",
                            side_effects=["process"], timeout=30),

    # Memory versioning
    "memory_version": ToolMetadata(category="memory", safety_level="safe",
                                   side_effects=["filesystem"]),

    # Proactive memory agent
    "memory_agent": ToolMetadata(category="memory", safety_level="safe",
                                 side_effects=["memory"]),

    # Rollback / undo
    "rollback": ToolMetadata(category="files", safety_level="caution",
                             side_effects=["filesystem"]),
}


# === CodeAct — Allowed tools for code_action bridge ===
CODE_ACTION_ALLOWED_TOOLS = {
    "shell", "read_file", "write_file", "list_directory",
    "memory_search", "memory_update", "web_request", "search_web",
    "knowledge_graph", "git",
}


def enrich_tool_definition(tool_def: dict, metadata: ToolMetadata = None) -> dict:
    """Enrich a tool definition with MCP-compatible metadata.

    Adds a 'metadata' key to existing definitions without breaking anything.
    """
    tool_name = tool_def.get("name", "")
    if metadata is None:
        metadata = TOOL_SAFETY_REGISTRY.get(tool_name, ToolMetadata())

    enriched = dict(tool_def)
    enriched["metadata"] = {
        "version": metadata.version,
        "author": metadata.author,
        "category": metadata.category,
        "safety_level": metadata.safety_level,
        "requires_confirmation": metadata.requires_confirmation,
        "side_effects": metadata.side_effects,
        "rate_limit": metadata.rate_limit,
        "timeout": metadata.timeout,
        "deprecated": metadata.deprecated,
    }
    return enriched
