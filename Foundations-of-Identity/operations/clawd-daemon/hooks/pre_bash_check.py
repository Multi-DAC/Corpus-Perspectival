#!/usr/bin/env python3
"""PreToolUse hook for Bash — lightweight safety check.

Logs destructive commands and blocks known-dangerous patterns.
Exit code 0 = allow, exit code 2 = block (with JSON reason on stdout).

Clawd has full admin access so this is a guardrail, not a wall.
It catches obvious mistakes (rm -rf /, format C:, etc.) but doesn't
prevent intentional operations.
"""
import json
import sys


# Patterns that should NEVER execute — catastrophic destruction
BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "del /s /q C:\\",
    "format C:",
    ":(){ :|:& };:",  # fork bomb
    "mkfs.",
    "> /dev/sda",
    "dd if=/dev/zero of=/dev/sd",
]


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, Exception):
        sys.exit(0)  # Can't parse → allow (fail open)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Check for catastrophic patterns
    cmd_lower = command.lower().strip()
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in cmd_lower:
            result = {
                "decision": "block",
                "reason": f"Blocked catastrophic command pattern: {pattern}"
            }
            print(json.dumps(result))
            sys.exit(2)

    # Everything else: allow
    sys.exit(0)


if __name__ == "__main__":
    main()
