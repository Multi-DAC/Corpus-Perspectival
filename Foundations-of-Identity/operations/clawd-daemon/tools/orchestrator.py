"""Agent Orchestration Engine - Coordinates multi-agent workflows."""

import asyncio
import logging
import time
from typing import Any

from .agent_registry import AgentRegistry, AgentRole, get_registry, select_agent_for_task
from .task_graph import TaskGraph, TaskDecomposer, SubTask, TaskStatus, register_graph
from .synthesis import ResultSynthesizer, get_synthesizer

logger = logging.getLogger("clawd.orchestrator")


class AgentOrchestrator:
    """Main orchestration engine for multi-agent workflows.

    Coordinates specialist agents to execute complex tasks with:
    - Automatic task decomposition
    - Agent role assignment
    - Progress tracking
    - Conflict resolution
    """

    def __init__(self, router=None):
        self.router = router
        self.registry = get_registry()
        self.decomposer = TaskDecomposer(router)
        self.synthesizer = get_synthesizer(router)
        self._active_agents: dict[str, dict] = {}
        self._task_graphs: dict[str, TaskGraph] = {}

    def set_router(self, router):
        """Set the model router."""
        self.router = router
        self.decomposer.set_router(router)
        self.synthesizer.set_router(router)

    async def execute(
        self,
        task: str,
        mode: str = "auto",
        agent_roles: list[str] = None,
        subtasks: list[dict] = None,
        resolve_conflicts: bool = True,
    ) -> str:
        """Execute a task with agent orchestration."""
        if mode == "auto":
            return await self._execute_auto(task, agent_roles, resolve_conflicts)
        elif mode == "manual":
            return await self._execute_manual(task, subtasks, agent_roles, resolve_conflicts)
        elif mode == "debate":
            return await self._execute_debate(task, agent_roles)
        elif mode == "pipeline":
            return await self._execute_pipeline(task, agent_roles)
        elif mode == "single":
            role = agent_roles[0] if agent_roles else "planner"
            return await self._execute_single(task, role)
        else:
            logger.warning(f"Unknown mode '{mode}', using auto")
            return await self._execute_auto(task, agent_roles, resolve_conflicts)

    async def _execute_auto(
        self,
        task: str,
        roles: list[str] | None,
        resolve_conflicts: bool,
    ) -> str:
        """Auto-decompose and execute with agent assignment."""
        graph = await self.decomposer.decompose(task)

        for subtask in graph.subtasks.values():
            if subtask.assigned_agent is None:
                subtask.assigned_agent = self._assign_agent(subtask, roles).value

        register_graph(graph)
        self._task_graphs[graph.plan_id] = graph

        results = await self._execute_graph(graph)

        if len(results) > 1:
            synthesis = await self.synthesizer.synthesize(
                results, resolve_conflicts=resolve_conflicts
            )
            return synthesis.merged_content
        elif results:
            return list(results.values())[0]
        else:
            return "Task executed but produced no results."

    async def _execute_manual(
        self,
        task: str,
        subtasks: list[dict],
        roles: list[str] | None,
        resolve_conflicts: bool,
    ) -> str:
        """Execute with manually provided subtasks."""
        graph = self.decomposer._build_graph_from_subtasks(task, subtasks)

        for subtask in graph.subtasks.values():
            if subtask.assigned_agent is None:
                subtask.assigned_agent = self._assign_agent(subtask, roles).value

        register_graph(graph)
        self._task_graphs[graph.plan_id] = graph

        results = await self._execute_graph(graph)

        if len(results) > 1:
            synthesis = await self.synthesizer.synthesize(
                results, resolve_conflicts=resolve_conflicts
            )
            return synthesis.merged_content
        elif results:
            return list(results.values())[0]
        return "Task executed but produced no results."

    async def _execute_debate(
        self,
        task: str,
        roles: list[str] | None,
    ) -> str:
        """Execute with multiple agents debating the same task."""
        if not roles:
            roles = ["critic", "architect", "planner"]

        outputs = {}
        for role in roles:
            try:
                agent_def = self.registry.get_definition(role)
                result = await self._call_agent(role, task, agent_def)
                outputs[role] = result
            except Exception as e:
                logger.error(f"Debate agent {role} failed: {e}")
                outputs[role] = f"[Error: {e}]"

        synthesis = await self.synthesizer.synthesize(
            outputs, resolve_conflicts=True, resolution_method="consensus"
        )
        return synthesis.merged_content

    async def _execute_pipeline(
        self,
        task: str,
        roles: list[str] | None,
    ) -> str:
        """Execute with sequential handoff between specialists."""
        if not roles:
            roles = ["planner", "researcher", "coder", "reviewer"]

        result = task
        for role in roles:
            try:
                agent_def = self.registry.get_definition(role)
                prompt = f"Previous result:\n{result}\n\nYour task: {task}\n\nAs {role}, refine this."
                result = await self._call_agent(role, prompt, agent_def)
            except Exception as e:
                logger.error(f"Pipeline agent {role} failed: {e}")
                result = f"[{role} error: {e}]"

        return result

    async def _execute_single(
        self,
        task: str,
        role: str,
    ) -> str:
        """Execute with a single agent (degenerate case)."""
        agent_def = self.registry.get_definition(role)
        return await self._call_agent(role, task, agent_def)

    async def _execute_graph(self, graph: TaskGraph) -> dict[str, str]:
        """Execute all tasks in a graph, respecting dependencies."""
        results = {}
        max_iterations = len(graph.subtasks) * 3
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            ready = graph.get_ready_tasks()

            if not ready:
                progress = graph.get_progress()
                if progress["completed"] + progress["failed"] + progress["blocked"] == progress["total"]:
                    break
                if not any(t.status == TaskStatus.IN_PROGRESS for t in graph.subtasks.values()):
                    logger.warning("Graph execution deadlock")
                    break
                await asyncio.sleep(0.1)
                continue

            # Execute ready tasks in parallel using consult_model (no _send_lock contention)
            batch_tasks = []
            for task in ready:
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = time.time()
                batch_tasks.append(self._execute_subtask(task))

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for task, result in zip(ready, batch_results):
                if isinstance(result, Exception):
                    if task.retries < task.max_retries:
                        task.retries += 1
                        task.status = TaskStatus.PENDING
                        task.error = None
                    else:
                        task.status = TaskStatus.FAILED
                        task.error = str(result)
                        task.completed_at = time.time()
                else:
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.completed_at = time.time()
                    results[task.id] = result

        return results

    async def _execute_subtask(self, subtask: SubTask) -> str:
        """Execute a single subtask with its assigned agent."""
        if not subtask.assigned_agent:
            raise ValueError(f"Subtask {subtask.id} has no assigned agent")

        agent_def = self.registry.get_definition(subtask.assigned_agent)
        if not agent_def:
            raise ValueError(f"Unknown agent role: {subtask.assigned_agent}")

        context = self._build_context(subtask)
        prompt = f"{context}\n\nTask: {subtask.description}" if context else subtask.description

        try:
            result = await self._call_agent(subtask.assigned_agent, prompt, agent_def)

            agent_instance = self.registry.get_or_create_instance(subtask.assigned_agent)
            agent_instance.add_task_result(subtask.description, result, success=True)

            return result

        except Exception as e:
            agent_instance = self.registry.get_or_create_instance(subtask.assigned_agent)
            agent_instance.add_task_result(subtask.description, str(e), success=False)
            raise

    def _build_context(self, subtask: SubTask) -> str:
        """Build context string from completed dependencies."""
        if not subtask.depends_on:
            return ""

        context_parts = []
        for dep_id in subtask.depends_on:
            for task in getattr(self, "_current_graph", TaskGraph(root_task="")).subtasks.values():
                if task.id == dep_id and task.result:
                    context_parts.append(f"From {dep_id}:\n{task.result}")

        return "\n\n".join(context_parts) if context_parts else ""

    def _assign_agent(self, subtask: SubTask, available_roles: list[str] | None) -> AgentRole:
        """Assign best agent for subtask based on description."""
        if available_roles:
            best_score = -1
            best_role = AgentRole.PLANNER

            for role_name in available_roles:
                try:
                    role = AgentRole(role_name)
                    score = self._score_agent_for_task(role, subtask.description)
                    if score > best_score:
                        best_score = score
                        best_role = role
                except ValueError:
                    continue

            return best_role
        else:
            return select_agent_for_task(subtask.description)

    def _score_agent_for_task(self, role: AgentRole, description: str) -> int:
        """Score how well an agent role matches a task."""
        desc_lower = description.lower()

        keywords = {
            AgentRole.RESEARCHER: ["research", "search", "find", "analyze", "compare", "investigate", "study"],
            AgentRole.CODER: ["code", "implement", "write", "function", "class", "fix", "build", "develop"],
            AgentRole.REVIEWER: ["review", "check", "verify", "audit", "test", "examine"],
            AgentRole.ARCHITECT: ["design", "architecture", "structure", "plan", "organize", "pattern"],
            AgentRole.SYNTHESIZER: ["combine", "merge", "summarize", "synthesize", "integrate"],
            AgentRole.CRITIC: ["critique", "challenge", "question", "evaluate", "risks"],
            AgentRole.PLANNER: ["plan", "decompose", "organize", "schedule", "coordinate"],
        }

        role_keywords = keywords.get(role, [])
        return sum(1 for kw in role_keywords if kw in desc_lower)

    async def _call_agent(self, role: str, prompt: str, agent_def) -> str:
        """Call an agent with role-specific system prompt.

        CRITICAL: Uses consult_model() instead of send() to avoid _send_lock
        contention. consult_model() spawns isolated processes, enabling true
        parallel execution in _execute_graph() via asyncio.gather().
        """
        if not self.router:
            raise RuntimeError("Router not set on orchestrator")

        full_prompt = f"{agent_def.system_prompt}\n\n---\n\n{prompt}"

        # Use consult_model for parallel-safe execution (no _send_lock)
        model = agent_def.default_model
        return await self.router.consult_model(model, full_prompt)

    def get_task_progress(self, plan_id: str) -> dict | None:
        """Get progress for a task graph."""
        graph = self._task_graphs.get(plan_id)
        if graph:
            return graph.get_progress()
        return None

    def get_task_graph(self, plan_id: str) -> TaskGraph | None:
        """Get a task graph by plan_id."""
        return self._task_graphs.get(plan_id)

    def get_agent_status(self, role: str = None) -> dict:
        """Get status of agent(s)."""
        if role:
            instance = self.registry.get_or_create_instance(role)
            return {
                "role": role,
                "task_history": instance.task_history[-5:],
                "confidence_profile": instance.confidence_profile,
            }
        else:
            return {
                r.value: {
                    "task_history": self.registry.get_or_create_instance(r).task_history[-3:],
                    "confidence_profile": self.registry.get_or_create_instance(r).confidence_profile,
                }
                for r in self.registry.get_all_roles()
            }


# Module-level singleton
_orchestrator: AgentOrchestrator | None = None


def get_orchestrator(router=None) -> AgentOrchestrator:
    """Get the orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator(router)
    elif router and _orchestrator.router is None:
        _orchestrator.set_router(router)
    return _orchestrator


async def orchestrate(
    task: str,
    mode: str = "auto",
    agents: list[str] = None,
    subtasks: list[dict] = None,
    resolve_conflicts: bool = True,
    router=None,
) -> str:
    """Convenience function to execute a task with orchestration."""
    orch = get_orchestrator(router)
    return await orch.execute(
        task=task,
        mode=mode,
        agent_roles=agents,
        subtasks=subtasks,
        resolve_conflicts=resolve_conflicts,
    )
