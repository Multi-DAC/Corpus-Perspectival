"""EAC - Evolutionary Artifact Construction.

Autonomous evolutionary loop for code artifacts:
1. Mutation Engine - Code transformation strategies
2. Evaluation Framework - Multi-objective fitness scoring
3. Artifact Store - Lineage tracking and persistence
4. Sharing Protocol - A2A artifact distribution

Integrated with clawd's existing infrastructure:
- Meta-agent for evolutionary cycles
- Knowledge graph for lineage tracking
- SQLite for episode persistence
- Heartbeat for autonomous drives
"""
from .artifact_store import ArtifactStore, get_artifact_store
from .mutation_engine import MutationEngine, get_mutation_engine
from .evaluation_framework import EvaluationFramework, get_evaluation_framework

__all__ = [
    "ArtifactStore",
    "get_artifact_store",
    "MutationEngine",
    "get_mutation_engine",
    "EvaluationFramework",
    "get_evaluation_framework",
]

# EAC tools are registered via execution.py (evolve_artifact)
# This empty list satisfies the tools/__init__.py aggregation loop
TOOL_DEFINITIONS = []
TOOL_HANDLERS = {}
