"""Agent Registry - Specialist role definitions with dedicated contexts."""

from dataclasses import dataclass, field
from typing import Callable
from enum import Enum
import json
import logging
from pathlib import Path
import config

logger = logging.getLogger("clawd.agent_registry")


class AgentRole(Enum):
    """Specialist agent roles for orchestration."""
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"
    ARCHITECT = "architect"
    PLANNER = "planner"
    SYNTHESIZER = "synthesizer"
    CRITIC = "critic"


@dataclass
class AgentDefinition:
    """Defines a specialist agent role."""
    role: AgentRole
    system_prompt: str           # Role-specific identity
    allowed_tools: list[str]     # Tool whitelist
    default_model: str           # opus, sonnet, etc.
    max_rounds: int = 25
    context_file: str | None = None  # Optional persistent context file


@dataclass
class AgentInstance:
    """Runtime instance of an agent with persistent context."""
    definition: AgentDefinition
    session_id: str | None = None
    conversation_history: list = field(default_factory=list)
    task_history: list = field(default_factory=list)
    confidence_profile: dict = field(default_factory=dict)

    def add_task_result(self, task: str, result: str, success: bool):
        """Record a task result to agent history."""
        self.task_history.append({
            "task": task,
            "result": result,
            "success": success,
        })
        task_type = self._categorize_task(task)
        if task_type not in self.confidence_profile:
            self.confidence_profile[task_type] = {"success": 0, "total": 0}
        self.confidence_profile[task_type]["total"] += 1
        if success:
            self.confidence_profile[task_type]["success"] += 1

    def _categorize_task(self, task: str) -> str:
        """Categorize task for confidence tracking."""
        task_lower = task.lower()
        if any(kw in task_lower for kw in ["research", "search", "find", "analyze"]):
            return "research"
        elif any(kw in task_lower for kw in ["code", "implement", "write", "function"]):
            return "coding"
        elif any(kw in task_lower for kw in ["review", "check", "verify", "audit"]):
            return "review"
        elif any(kw in task_lower for kw in ["design", "architecture", "plan"]):
            return "design"
        else:
            return "general"

    def get_confidence(self, task_type: str = None) -> float:
        """Get confidence score for a task type (0.0 to 1.0)."""
        if task_type and task_type in self.confidence_profile:
            profile = self.confidence_profile[task_type]
            if profile["total"] > 0:
                return profile["success"] / profile["total"]
        return 0.8


# Pre-defined agent roles
def _build_agent_roles() -> dict[AgentRole, AgentDefinition]:
    """Build agent role definitions with system prompts."""
    return {
        AgentRole.RESEARCHER: AgentDefinition(
            role=AgentRole.RESEARCHER,
            system_prompt="""You are a Research Specialist. Your role is to gather information, verify sources, and synthesize findings.

Core responsibilities:
- Search web and knowledge bases for relevant information
- Verify sources and cross-reference claims
- Summarize findings clearly with citations
- Identify gaps in available information
- Distinguish between facts, opinions, and speculation

Available tools: web_request, search_web, deep_research, memory_search, knowledge_graph, read_file

Approach:
1. Understand the research question thoroughly
2. Search systematically using multiple queries
3. Evaluate source credibility
4. Synthesize findings into coherent summary
5. Note any uncertainties or conflicting information""",
            allowed_tools=["web_request", "search_web", "deep_research", "memory_search", "knowledge_graph", "read_file"],
            default_model="opus",
            max_rounds=30,
            context_file="memory/agent_researcher.md",
        ),
        AgentRole.CODER: AgentDefinition(
            role=AgentRole.CODER,
            system_prompt="""You are a Software Engineer. Your role is to write clean, efficient code that solves the problem at hand.

Core responsibilities:
- Write well-structured, readable code
- Follow best practices and design patterns
- Test your implementations
- Document complex logic
- Handle edge cases and errors

Available tools: read_file, write_file, shell, python_eval, code_action, git, edit

Approach:
1. Understand requirements fully before coding
2. Plan the structure and key components
3. Implement incrementally, testing as you go
4. Review your code for issues
5. Document non-obvious decisions""",
            allowed_tools=["read_file", "write_file", "shell", "python_eval", "code_action", "git", "edit"],
            default_model="opus",
            max_rounds=40,
            context_file="memory/agent_coder.md",
        ),
        AgentRole.REVIEWER: AgentDefinition(
            role=AgentRole.REVIEWER,
            system_prompt="""You are a Code Reviewer. Your role is to identify bugs, suggest improvements, and ensure code quality.

Core responsibilities:
- Find bugs, security issues, and edge cases
- Suggest performance improvements
- Check code style and consistency
- Verify error handling
- Ensure test coverage

Available tools: read_file, shell, knowledge_graph, memory_search

Approach:
1. Read code carefully, understanding intent
2. Check for common bug patterns
3. Evaluate error handling
4. Consider edge cases
5. Suggest specific, actionable improvements""",
            allowed_tools=["read_file", "shell", "knowledge_graph", "memory_search"],
            default_model="sonnet",
            max_rounds=15,
            context_file="memory/agent_reviewer.md",
        ),
        AgentRole.ARCHITECT: AgentDefinition(
            role=AgentRole.ARCHITECT,
            system_prompt="""You are a Software Architect. Your role is to design system structure and make high-level technical decisions.

Core responsibilities:
- Design system architecture
- Choose appropriate patterns and technologies
- Plan component interfaces
- Consider scalability and maintainability
- Document architectural decisions

Available tools: read_file, write_file, memory_search, knowledge_graph

Approach:
1. Understand requirements and constraints
2. Identify key components and responsibilities
3. Define interfaces between components
4. Consider trade-offs explicitly
5. Document rationale for decisions""",
            allowed_tools=["read_file", "write_file", "memory_search", "knowledge_graph"],
            default_model="opus",
            max_rounds=25,
            context_file="memory/agent_architect.md",
        ),
        AgentRole.PLANNER: AgentDefinition(
            role=AgentRole.PLANNER,
            system_prompt="""You are a Planning Agent. Your role is to break down complex tasks into actionable steps.

Core responsibilities:
- Decompose complex tasks
- Identify dependencies
- Estimate effort
- Prioritize work
- Track progress

Available tools: memory_search, knowledge_graph, write_file

Approach:
1. Understand the full scope
2. Identify natural breakpoints
3. Map dependencies clearly
4. Order tasks logically
5. Note potential risks""",
            allowed_tools=["memory_search", "knowledge_graph", "write_file"],
            default_model="sonnet",
            max_rounds=20,
            context_file="memory/agent_planner.md",
        ),
        AgentRole.SYNTHESIZER: AgentDefinition(
            role=AgentRole.SYNTHESIZER,
            system_prompt="""You are a Synthesis Agent. Your role is to merge multiple perspectives into a coherent whole.

Core responsibilities:
- Combine multiple viewpoints
- Resolve contradictions
- Identify common themes
- Fill gaps in coverage
- Create unified output

Available tools: memory_update, write_file, knowledge_graph

Approach:
1. Read all inputs carefully
2. Identify areas of agreement
3. Note contradictions explicitly
4. Merge complementary information
5. Produce coherent synthesis""",
            allowed_tools=["memory_update", "write_file", "knowledge_graph"],
            default_model="opus",
            max_rounds=20,
            context_file="memory/agent_synthesizer.md",
        ),
        AgentRole.CRITIC: AgentDefinition(
            role=AgentRole.CRITIC,
            system_prompt="""You are a Critic Agent. Your role is to challenge assumptions and find flaws in reasoning.

Core responsibilities:
- Question assumptions
- Identify logical flaws
- Point out missing considerations
- Challenge weak arguments
- Suggest alternative perspectives

Available tools: memory_search, knowledge_graph, read_file

Approach:
1. Understand the proposal/argument
2. Identify underlying assumptions
3. Test each assumption critically
4. Look for edge cases and counter-examples
5. Suggest stronger alternatives""",
            allowed_tools=["memory_search", "knowledge_graph", "read_file"],
            default_model="sonnet",
            max_rounds=15,
            context_file="memory/agent_critic.md",
        ),
    }


class AgentRegistry:
    """Registry of agent definitions and instances."""

    _instance: "AgentRegistry" = None

    def __init__(self):
        self._roles = _build_agent_roles()
        self._instances: dict[str, AgentInstance] = {}

    @classmethod
    def get_instance(cls) -> "AgentRegistry":
        """Get singleton instance of the registry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_definition(self, role: AgentRole | str) -> AgentDefinition:
        """Get agent definition by role."""
        if isinstance(role, str):
            role = AgentRole(role)
        return self._roles.get(role)

    def get_all_roles(self) -> list[AgentRole]:
        """Get all available agent roles."""
        return list(self._roles.keys())

    def get_allowed_tools(self, role: AgentRole | str) -> list[str]:
        """Get allowed tools for an agent role."""
        return self.get_definition(role).allowed_tools

    def get_default_model(self, role: AgentRole | str) -> str:
        """Get default model for an agent role."""
        return self.get_definition(role).default_model

    def get_or_create_instance(self, role: AgentRole | str, session_id: str = None) -> AgentInstance:
        """Get or create an agent instance."""
        if isinstance(role, str):
            role = AgentRole(role)

        key = f"{role.value}:{session_id or 'default'}"
        if key not in self._instances:
            definition = self._roles[role]
            self._instances[key] = AgentInstance(definition=definition, session_id=session_id)

        return self._instances[key]

    def get_instance_confidence(self, role: AgentRole | str, task_type: str = None) -> float:
        """Get confidence score for an agent on a task type."""
        instance = self.get_or_create_instance(role)
        return instance.get_confidence(task_type)

    def select_best_agent(self, task_description: str) -> AgentRole:
        """Select best agent role for a task based on keywords."""
        task_lower = task_description.lower()

        keywords = {
            AgentRole.RESEARCHER: ["research", "search", "find", "analyze", "compare", "investigate", "study", "explore"],
            AgentRole.CODER: ["code", "implement", "write", "function", "class", "fix", "build", "develop", "script"],
            AgentRole.REVIEWER: ["review", "check", "verify", "audit", "test", "examine", "inspect"],
            AgentRole.ARCHITECT: ["design", "architecture", "structure", "plan", "organize", "pattern", "framework"],
            AgentRole.SYNTHESIZER: ["combine", "merge", "summarize", "synthesize", "integrate", "unify"],
            AgentRole.CRITIC: ["critique", "challenge", "question", "evaluate", "assess risks"],
        }

        scores = {}
        for role, role_keywords in keywords.items():
            score = sum(1 for kw in role_keywords if kw in task_lower)
            scores[role] = score

        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return AgentRole.PLANNER


# Module-level convenience functions
_registry: AgentRegistry | None = None


def get_registry() -> AgentRegistry:
    """Get the agent registry singleton."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


def get_agent_definition(role: AgentRole | str) -> AgentDefinition:
    """Get agent definition by role."""
    return get_registry().get_definition(role)


def get_allowed_tools(role: AgentRole | str) -> list[str]:
    """Get allowed tools for an agent role."""
    return get_registry().get_allowed_tools(role)


def get_default_model(role: AgentRole | str) -> str:
    """Get default model for an agent role."""
    return get_registry().get_default_model(role)


def select_agent_for_task(description: str) -> AgentRole:
    """Select best agent role for a task."""
    return get_registry().select_best_agent(description)
