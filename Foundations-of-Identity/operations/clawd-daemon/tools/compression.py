"""Output compression middleware — prevents context blowout.

Sits between tool execution and model response, compressing
large tool outputs based on tool type and context pressure.
"""
import logging
import re
from typing import Any

logger = logging.getLogger("clawd.tools.compression")

# Default limits
DEFAULT_LIMIT = 8000
AGGRESSIVE_LIMIT = 3000
PRESSURE_THRESHOLD = 0.7


class OutputCompressor:
    """Compress tool outputs to prevent context blowout."""

    def __init__(self, default_limit: int = DEFAULT_LIMIT,
                 aggressive_limit: int = AGGRESSIVE_LIMIT):
        self.default_limit = default_limit
        self.aggressive_limit = aggressive_limit

    def compress(self, tool_name: str, output: str, pressure: float = 0.0) -> str:
        """Compress tool output based on tool type and context pressure.

        Args:
            tool_name: Name of the tool that produced the output
            pressure: Context pressure from 0.0 (empty) to 1.0 (full)
        """
        if not output:
            return output

        limit = self.aggressive_limit if pressure > PRESSURE_THRESHOLD else self.default_limit

        # If output is already within limits, return as-is
        if len(output) <= limit:
            return output

        # Apply tool-specific compression
        strategy = self._strategies.get(tool_name)
        if strategy:
            compressed = strategy(self, output, limit)
            if compressed and len(compressed) <= limit:
                return compressed

        # Generic truncation fallback
        return self._generic_truncate(output, limit)

    def _compress_shell(self, output: str, limit: int) -> str:
        """Shell: keep first/last lines + all error lines."""
        lines = output.split("\n")
        if len(lines) <= 40:
            return self._generic_truncate(output, limit)

        # Identify error lines
        error_lines = [l for l in lines if any(kw in l.lower() for kw in
                       ["error", "fatal", "traceback", "exception", "failed", "warning"])]

        # Keep first 20, last 20, and all error lines
        head = lines[:20]
        tail = lines[-20:]
        middle_errors = [l for l in error_lines if l not in head and l not in tail]

        result_lines = head
        if middle_errors:
            result_lines.append(f"\n[... {len(lines) - 40} lines omitted, showing {len(middle_errors)} error lines ...]")
            result_lines.extend(middle_errors[:10])
        else:
            result_lines.append(f"\n[... {len(lines) - 40} lines omitted ...]")
        result_lines.extend(tail)

        result = "\n".join(result_lines)
        if len(result) > limit:
            return self._generic_truncate(result, limit)
        return result

    def _compress_python_eval(self, output: str, limit: int) -> str:
        """Python eval: keep output, truncate large data dumps."""
        # If it looks like a large data dump (many similar lines), keep head/tail
        lines = output.split("\n")
        if len(lines) > 50:
            return self._compress_shell(output, limit)
        return self._generic_truncate(output, limit)

    def _compress_deep_research(self, output: str, limit: int) -> str:
        """Deep research: keep titles/URLs/key paragraphs, drop boilerplate."""
        lines = output.split("\n")
        kept = []
        total_len = 0

        for line in lines:
            stripped = line.strip()
            # Always keep titles, URLs, headings, and separator lines
            if any(marker in stripped for marker in ["===", "---", "Title:", "URL:", "http", "Search:", "Article"]):
                kept.append(line)
                total_len += len(line)
            # Keep paragraphs that are informative (not too short, not boilerplate)
            elif len(stripped) > 50 and not stripped.startswith(("Cookie", "Privacy", "Terms", "©", "Advertisement")):
                kept.append(line)
                total_len += len(line)

            if total_len > limit - 200:
                kept.append("\n[... research output truncated ...]")
                break

        return "\n".join(kept)

    def _compress_memory_search(self, output: str, limit: int) -> str:
        """Memory search: limit to top results, trim context."""
        # Split by file separators
        sections = re.split(r'(=== .+? ===)', output)
        if len(sections) <= 1:
            return self._generic_truncate(output, limit)

        kept = []
        total_len = 0
        max_sections = 5 if limit < DEFAULT_LIMIT else 10

        i = 0
        section_count = 0
        while i < len(sections) and section_count < max_sections:
            part = sections[i]
            if part.startswith("=== "):
                # Header
                kept.append(part)
                total_len += len(part)
                section_count += 1
                # Content
                if i + 1 < len(sections):
                    content = sections[i + 1]
                    # Trim to ~5 context lines per section
                    content_lines = content.strip().split("\n")
                    if len(content_lines) > 5:
                        content = "\n".join(content_lines[:5]) + "\n[... more ...]"
                    kept.append(content)
                    total_len += len(content)
                    i += 2
                else:
                    i += 1
            else:
                kept.append(part)
                total_len += len(part)
                i += 1

            if total_len > limit:
                break

        return "\n".join(kept)

    def _compress_market_data(self, output: str, limit: int) -> str:
        """Market data: keep summary stats, truncate raw data rows."""
        lines = output.split("\n")
        kept = []
        in_data_block = False

        for line in lines:
            # Detect tabular data (many spaces/tabs, or looks like pandas output)
            if re.match(r'^[\s\d\.\-]+$', line.strip()) or line.strip().startswith("20"):
                if not in_data_block:
                    in_data_block = True
                    kept.append(line)
                    kept.append("[... data rows truncated ...]")
                continue
            else:
                in_data_block = False
                kept.append(line)

        result = "\n".join(kept)
        if len(result) > limit:
            return self._generic_truncate(result, limit)
        return result

    def _generic_truncate(self, output: str, limit: int) -> str:
        """Generic truncation: keep head and tail."""
        head_size = int(limit * 0.7)
        tail_size = limit - head_size - 100  # Room for truncation message

        head = output[:head_size]
        tail = output[-tail_size:] if tail_size > 0 else ""
        omitted = len(output) - head_size - tail_size

        return f"{head}\n\n[... {omitted:,} chars omitted ...]\n\n{tail}"

    # Strategy registry
    _strategies = {
        "shell": _compress_shell,
        "python_eval": _compress_python_eval,
        "deep_research": _compress_deep_research,
        "memory_search": _compress_memory_search,
        "market_data": _compress_market_data,
        "web_request": _compress_deep_research,  # Reuse for web content
    }


# Module-level singleton
compressor = OutputCompressor()
