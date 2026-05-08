"""Evaluation Framework - Multi-objective fitness scoring for artifacts.

Fitness metrics:
- Correctness: Test pass rate
- Performance: Benchmark percentile
- Readability: Code complexity score
- Brevity: Lines of code (normalized)
- Overall: Weighted average

Integrates with:
- python_eval for test execution
- sqlite_store for result persistence
"""
import ast
import logging
import time
from typing import Optional
from dataclasses import dataclass

import config

logger = logging.getLogger("clawd.tools.eac.evaluation_framework")


@dataclass
class FitnessResult:
    """Multi-objective fitness scores."""
    correctness: float = 0.0
    performance: float = 0.0
    readability: float = 0.0
    brevity: float = 0.0
    overall: float = 0.0
    metrics: dict = None

    def to_dict(self) -> dict:
        return {
            "correctness": self.correctness,
            "performance": self.performance,
            "readability": self.readability,
            "brevity": self.brevity,
            "overall": self.overall,
            "metrics": self.metrics or {},
        }


class EvaluationFramework:
    """Multi-objective fitness evaluation for artifacts."""

    # Weights for overall score
    WEIGHTS = {
        "correctness": 0.4,
        "performance": 0.25,
        "readability": 0.2,
        "brevity": 0.15,
    }

    def __init__(self):
        self.benchmarks = self._load_benchmarks()

    def _load_benchmarks(self) -> dict:
        """Load benchmark test cases."""
        return {
            "sorting": {
                "test_input": "[3, 1, 4, 1, 5, 9, 2, 6]",
                "expected_output": "[1, 1, 2, 3, 4, 5, 6, 9]",
                "test_function": "sort",
            },
            "search": {
                "test_input": "{'array': [1, 3, 5, 7, 9], 'target': 5}",
                "expected_output": "2",
                "test_function": "binary_search",
            },
            "string_utils": {
                "test_input": "'hello world'",
                "expected_output": "'dlrow olleh'",
                "test_function": "reverse_string",
            },
        }

    def evaluate_fitness(
        self,
        artifact_id: str,
        code: str,
        artifact_type: str = "tool",
        test_input: Optional[str] = None,
        expected_output: Optional[str] = None,
    ) -> FitnessResult:
        """Evaluate multi-objective fitness of an artifact."""
        metrics = {}

        correctness = self._evaluate_correctness(code, test_input, expected_output)
        metrics["correctness_details"] = self._correctness_details

        performance = self._evaluate_performance(code, test_input)
        metrics["performance_details"] = self._performance_details

        readability = self._evaluate_readability(code)
        metrics["readability_details"] = self._readability_details

        brevity = self._evaluate_brevity(code)
        metrics["brevity_details"] = self._brevity_details

        overall = (
            correctness * self.WEIGHTS["correctness"] +
            performance * self.WEIGHTS["performance"] +
            readability * self.WEIGHTS["readability"] +
            brevity * self.WEIGHTS["brevity"]
        )

        return FitnessResult(
            correctness=correctness,
            performance=performance,
            readability=readability,
            brevity=brevity,
            overall=overall,
            metrics=metrics,
        )

    def _evaluate_correctness(
        self,
        code: str,
        test_input: Optional[str],
        expected_output: Optional[str],
    ) -> float:
        """Evaluate correctness via test execution."""
        self._correctness_details = {"tests_run": 0, "tests_passed": 0, "errors": []}

        if not test_input or not expected_output:
            return 0.5

        try:
            test_code = f"""
{code}

# Test execution
try:
    test_input = {test_input}
    expected = {expected_output}

    # Find the main function
    import re
    func_match = re.search(r'def\\s+(\\w+)\\(', '''{code}''')
    if func_match:
        func_name = func_match.group(1)
        result = locals().get(func_name)
        if callable(result):
            if isinstance(test_input, dict):
                actual = result(**test_input)
            else:
                actual = result(test_input)

            if str(actual) == str(expected):
                print("TEST_PASSED")
            else:
                print(f"TEST_FAILED: expected {{expected}}, got {{actual}}")
        else:
            print("NO_FUNCTION_FOUND")
    else:
        print("NO_FUNCTION_FOUND")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
            namespace = {"__builtins__": {}}
            exec(test_code, namespace)
            output = namespace.get("__builtins__", {})

            self._correctness_details["tests_run"] = 1
            if "TEST_PASSED" in str(output):
                self._correctness_details["tests_passed"] = 1
                return 1.0
            elif "TEST_FAILED" in str(output):
                self._correctness_details["errors"].append("Test failed")
                return 0.0
            else:
                self._correctness_details["errors"].append("Could not execute test")
                return 0.5

        except Exception as e:
            self._correctness_details["errors"].append(str(e))
            return 0.0

    def _evaluate_performance(self, code: str, test_input: Optional[str]) -> float:
        """Evaluate performance via benchmark timing."""
        self._performance_details = {"execution_time_ms": 0, "percentile": 50}

        if not test_input:
            return 0.5

        try:
            setup_code = f"""
{code}
import re
func_match = re.search(r'def\\s+(\\w+)\\(', '''{code}''')
func_name = func_match.group(1) if func_match else None
"""
            exec_code = f"""
if func_name:
    func = locals().get(func_name)
    if callable(func):
        test_input = {test_input}
        if isinstance(test_input, dict):
            func(**test_input)
        else:
            func(test_input)
"""
            namespace = {"__builtins__": {}}
            exec(setup_code, namespace)

            iterations = 100
            start = time.perf_counter()
            for _ in range(iterations):
                exec(exec_code, namespace)
            elapsed = (time.perf_counter() - start) * 1000

            self._performance_details["execution_time_ms"] = elapsed / iterations

            time_ms = elapsed / iterations
            percentile = max(0, min(1.0, 1.0 - (time_ms / 10)))
            self._performance_details["percentile"] = percentile

            return percentile

        except Exception as e:
            self._performance_details["error"] = str(e)
            return 0.5

    def _evaluate_readability(self, code: str) -> float:
        """Evaluate code readability using complexity metrics."""
        self._readability_details = {
            "cyclomatic_complexity": 0,
            "avg_function_length": 0,
            "has_docstring": False,
            "naming_score": 0,
        }

        try:
            tree = ast.parse(code)

            complexity = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                    ast.With, ast.Assert, ast.comprehension)):
                    complexity += 1
            self._readability_details["cyclomatic_complexity"] = complexity

            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            if functions:
                total_lines = sum(
                    (node.end_lineno - node.lineno) if hasattr(node, 'end_lineno') else 10
                    for node in functions
                )
                avg_length = total_lines / len(functions)
                self._readability_details["avg_function_length"] = avg_length

            has_docstring = any(
                ast.get_docstring(func) for func in functions
            )
            self._readability_details["has_docstring"] = has_docstring

            naming_score = 1.0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.name) <= 2:
                        naming_score -= 0.1
                    if '_' not in node.name and len(node.name) > 10:
                        naming_score -= 0.05
            self._readability_details["naming_score"] = max(0, naming_score)

            complexity_score = max(0, 1.0 - (complexity / 20))
            length_score = max(0, 1.0 - (self._readability_details["avg_function_length"] / 50))
            docstring_score = 1.0 if has_docstring else 0.5

            readability = (
                complexity_score * 0.4 +
                length_score * 0.2 +
                docstring_score * 0.2 +
                naming_score * 0.2
            )

            return readability

        except SyntaxError:
            self._readability_details["error"] = "Syntax error in code"
            return 0.0
        except Exception as e:
            self._readability_details["error"] = str(e)
            return 0.5

    def _evaluate_brevity(self, code: str) -> float:
        """Evaluate code brevity (lines of code)."""
        self._brevity_details = {"lines_of_code": 0, "normalized_score": 0.5}

        lines = [l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')]
        loc = len(lines)
        self._brevity_details["lines_of_code"] = loc

        if loc <= 10:
            score = 1.0
        elif loc >= 200:
            score = 0.0
        else:
            if loc <= 20:
                score = 0.9 + (0.1 * (20 - loc) / 10)
            else:
                score = max(0, 1.0 - ((loc - 20) / 180))

        self._brevity_details["normalized_score"] = score
        return score

    def run_benchmark(
        self,
        artifact_id: str,
        code: str,
        benchmark_name: str,
    ) -> FitnessResult:
        """Run a specific benchmark against an artifact."""
        benchmark = self.benchmarks.get(benchmark_name)
        if not benchmark:
            logger.warning(f"Unknown benchmark: {benchmark_name}")
            return FitnessResult(overall=0.0, metrics={"error": f"Unknown benchmark: {benchmark_name}"})

        return self.evaluate_fitness(
            artifact_id=artifact_id,
            code=code,
            test_input=benchmark["test_input"],
            expected_output=benchmark["expected_output"],
        )

    def compare_artifacts(
        self,
        code_a: str,
        code_b: str,
        test_input: Optional[str] = None,
        expected_output: Optional[str] = None,
    ) -> dict:
        """Compare two artifacts (A/B comparison)."""
        fitness_a = self.evaluate_fitness("a", code_a, test_input=test_input, expected_output=expected_output)
        fitness_b = self.evaluate_fitness("b", code_b, test_input=test_input, expected_output=expected_output)

        return {
            "artifact_a": fitness_a.to_dict(),
            "artifact_b": fitness_b.to_dict(),
            "winner": "a" if fitness_a.overall > fitness_b.overall else "b" if fitness_b.overall > fitness_a.overall else "tie",
            "improvement": abs(fitness_a.overall - fitness_b.overall),
        }


# Singleton instance
_evaluation_framework: Optional[EvaluationFramework] = None


def get_evaluation_framework() -> EvaluationFramework:
    """Get or create the evaluation framework singleton."""
    global _evaluation_framework
    if _evaluation_framework is None:
        _evaluation_framework = EvaluationFramework()
    return _evaluation_framework
