"""Mutation Engine - Code transformation strategies for artifact evolution.

Implements various mutation strategies:
- Rename variables/functions
- Extract functions
- Inline code
- Optimize loops
- Add/remove comments
- Simplify logic
- Expand functionality

Integrates with:
- tool_factory.py for sandboxed execution
- create_tool for runtime tool creation
"""
import ast
import logging
import random
import re
from typing import Optional

logger = logging.getLogger("clawd.tools.eac.mutation_engine")


class MutationEngine:
    """Applies mutations to code artifacts."""

    def __init__(self):
        self.strategies = {
            "rename": self._rename_variables,
            "refactor": self._extract_function,
            "optimize": self._optimize_loop,
            "simplify": self._simplify_logic,
            "expand": self._expand_functionality,
            "comment": self._modify_comments,
            "inline": self._inline_code,
            "crossover": self._crossover,
        }

    def mutate_code(
        self,
        artifact_id: str,
        code: str,
        strategy: str = "rename",
        parameters: Optional[dict] = None,
    ) -> tuple[str, dict]:
        """Apply a mutation strategy to code.

        Args:
            artifact_id: Source artifact ID
            code: Source code to mutate
            strategy: Mutation strategy name
            parameters: Strategy-specific parameters

        Returns:
            tuple of (mutated_code, mutation_metadata)
        """
        if strategy not in self.strategies:
            logger.warning(f"Unknown mutation strategy: {strategy}")
            return code, {"error": f"Unknown strategy: {strategy}"}

        try:
            mutator = self.strategies[strategy]
            mutated, metadata = mutator(code, parameters or {})
            metadata["strategy"] = strategy
            metadata["source_artifact"] = artifact_id
            return mutated, metadata
        except Exception as e:
            logger.error(f"Mutation failed ({strategy}): {e}")
            return code, {"error": str(e), "strategy": strategy}

    def _rename_variables(self, code: str, params: dict) -> tuple[str, dict]:
        """Rename variables to more descriptive names."""
        renamed = code
        changes = []

        var_mappings = {
            r'\bi\b': 'index',
            r'\bj\b': 'inner_index',
            r'\bk\b': 'outer_index',
            r'\bn\b': 'count',
            r'\bx\b': 'value',
            r'\by\b': 'result',
            r'\btemp\b': 'temporary',
            r'\btmp\b': 'temporary',
            r'\barr\b': 'array',
            r'\blst\b': 'items',
            r'\bdct\b': 'mapping',
            r'\bfn\b': 'function',
            r'\bres\b': 'result',
        }

        for pattern, replacement in var_mappings.items():
            matches = len(re.findall(pattern, renamed))
            if matches > 0:
                renamed = re.sub(pattern, replacement, renamed)
                changes.append(f"{pattern} -> {replacement} ({matches}x)")

        return renamed, {
            "type": "rename",
            "changes": changes,
            "num_changes": len(changes),
        }

    def _extract_function(self, code: str, params: dict) -> tuple[str, dict]:
        """Extract a code block into a separate function."""
        lines = code.split('\n')

        for i, line in enumerate(lines):
            if line.strip().startswith('for ') and ':' in line:
                indent = len(line) - len(line.lstrip())
                body_start = i + 1
                body_lines = []

                for j in range(body_start, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' ' * (indent + 1)):
                        break
                    body_lines.append(lines[j])

                if body_lines:
                    func_name = params.get("func_name", f"extracted_block_{i}")
                    func_def = f"{' ' * indent}def {func_name}():\n"
                    func_body = '\n'.join('    ' + bl if bl.strip() else bl for bl in body_lines)
                    func_def += func_body + '\n'

                    new_lines = lines[:body_start] + [f"{' ' * (indent + 4)}{func_name}()"] + lines[j:]
                    new_code = '\n'.join(new_lines)

                    return func_def + '\n' + new_code, {
                        "type": "refactor",
                        "extracted_function": func_name,
                        "lines_extracted": len(body_lines),
                    }

        return code, {"type": "refactor", "no_suitable_block": True}

    def _optimize_loop(self, code: str, params: dict) -> tuple[str, dict]:
        """Optimize loop patterns."""
        optimized = code
        changes = []

        pattern1 = r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\)'
        match = re.search(pattern1, optimized)
        if match:
            idx_var = match.group(1)
            list_var = match.group(2)
            replacement = f"for {idx_var}, {list_var}_item in enumerate({list_var})"
            optimized = re.sub(pattern1, replacement, optimized)
            changes.append("Converted range(len()) to enumerate()")

        pattern2 = r'for\s+(\w+)\s+in\s+(\w+):\s*\1_result\.append\((\w+)\)'
        match = re.search(pattern2, optimized)
        if match:
            changes.append("Detected append loop - consider list comprehension")

        return optimized, {
            "type": "optimize",
            "changes": changes,
            "num_optimizations": len(changes),
        }

    def _simplify_logic(self, code: str, params: dict) -> tuple[str, dict]:
        """Simplify complex logic patterns."""
        simplified = code
        changes = []

        pattern1 = r'if\s+(.+):\s*return\s+True\s*else:\s*return\s+False'
        match = re.search(pattern1, simplified)
        if match:
            condition = match.group(1)
            replacement = f"return {condition}"
            simplified = re.sub(pattern1, replacement, simplified)
            changes.append("Simplified boolean return")

        pattern2 = r'not\s+\(([^)]+)\s+and\s+([^)]+)\)'
        if re.search(pattern2, simplified):
            changes.append("Detected De Morgan opportunity")

        return simplified, {
            "type": "simplify",
            "changes": changes,
        }

    def _expand_functionality(self, code: str, params: dict) -> tuple[str, dict]:
        """Expand functionality by adding features."""
        expanded = code
        additions = []

        if params.get("add_error_handling") and "try" not in code:
            lines = code.split('\n')
            wrapped = ["try:"]
            for line in lines:
                wrapped.append("    " + line if line.strip() else line)
            wrapped.append("except Exception as e:")
            wrapped.append("    return f\"[Error: {e}]\"")
            expanded = '\n'.join(wrapped)
            additions.append("Added error handling")

        if params.get("add_docstring") and '"""' not in code:
            lines = code.split('\n')
            docstring = f'    """Auto-generated function."""\n'
            for i, line in enumerate(lines):
                if 'def ' in line and ':' in line:
                    lines.insert(i + 1, docstring)
                    break
            expanded = '\n'.join(lines)
            additions.append("Added docstring")

        if params.get("add_type_hints"):
            pattern = r'def\s+(\w+)\(([^)]*)\):'
            match = re.search(pattern, expanded)
            if match and not ':' in match.group(2):
                func_name = match.group(1)
                args = match.group(2)
                if args.strip():
                    new_args = f"{args}: int"
                else:
                    new_args = ""
                replacement = f"def {func_name}({new_args}) -> str:"
                expanded = re.sub(pattern, replacement, expanded)
                additions.append("Added type hints")

        return expanded, {
            "type": "expand",
            "additions": additions,
        }

    def _modify_comments(self, code: str, params: dict) -> tuple[str, dict]:
        """Add, remove, or modify comments."""
        modified = code
        changes = []

        if params.get("add_comments"):
            lines = modified.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('def ') and i > 0:
                    func_name = line.split('def ')[1].split('(')[0]
                    comment = f"    # {func_name}: Auto-generated function\n"
                    lines.insert(i, comment)
            modified = '\n'.join(lines)
            changes.append("Added function comments")

        if params.get("remove_comments"):
            modified = re.sub(r'\s*#.*$', '', modified, flags=re.MULTILINE)
            changes.append("Removed comments")

        return modified, {
            "type": "comment",
            "changes": changes,
        }

    def _inline_code(self, code: str, params: dict) -> tuple[str, dict]:
        """Inline small functions."""
        pattern = r'def\s+(\w+)\((\w*)\):\s*return\s+(.+)\n'
        matches = list(re.finditer(pattern, code))

        if not matches or not params.get("target_function"):
            return code, {"type": "inline", "no_suitable_function": True}

        target = params.get("target_function")
        for match in matches:
            func_name = match.group(1)
            if func_name == target:
                return code, {
                    "type": "inline",
                    "inlinable_function": func_name,
                    "body": match.group(3),
                }

        return code, {"type": "inline", "function_not_found": target}

    def _crossover(self, code_a: str, params: dict) -> tuple[str, dict]:
        """Combine two code artifacts (crossover)."""
        code_b = params.get("code_b", "")
        if not code_b:
            return code_a, {"error": "code_b required for crossover"}

        functions_a = re.findall(r'(def\s+\w+\([^)]*\):.*?)(?=\ndef|\Z)', code_a, re.DOTALL)
        functions_b = re.findall(r'(def\s+\w+\([^)]*\):.*?)(?=\ndef|\Z)', code_b, re.DOTALL)

        combined = "# Crossover artifact\n\n"
        for func in functions_a + functions_b:
            combined += func + "\n\n"

        return combined, {
            "type": "crossover",
            "functions_from_a": len(functions_a),
            "functions_from_b": len(functions_b),
            "total_functions": len(functions_a) + len(functions_b),
        }

    def crossover(self, code_a: str, code_b: str, artifact_a: str, artifact_b: str) -> tuple[str, dict]:
        """Public crossover method combining two artifacts."""
        result, metadata = self._crossover(code_a, {"code_b": code_b})
        metadata["parent_a"] = artifact_a
        metadata["parent_b"] = artifact_b
        return result, metadata


# Singleton instance
_mutation_engine: Optional[MutationEngine] = None


def get_mutation_engine() -> MutationEngine:
    """Get or create the mutation engine singleton."""
    global _mutation_engine
    if _mutation_engine is None:
        _mutation_engine = MutationEngine()
    return _mutation_engine
