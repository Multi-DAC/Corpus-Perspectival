"""Task Decomposition Graph - DAG-based subtask tracking with dependencies."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import asyncio
import logging
import time
import uuid

logger = logging.getLogger("clawd.task_graph")


class TaskStatus(Enum):
    """Status of a subtask in the execution graph."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # Dependency failed


@dataclass
class SubTask:
    """A single subtask in the decomposition graph."""
    id: str
    description: str
    assigned_agent: str | None = None  # AgentRole value
    depends_on: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
    started_at: float | None = None
    completed_at: float | None = None
    retries: int = 0
    max_retries: int = 2

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "assigned_agent": self.assigned_agent,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "retries": self.retries,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SubTask":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            description=data["description"],
            assigned_agent=data.get("assigned_agent"),
            depends_on=data.get("depends_on", []),
            status=TaskStatus(data.get("status", "pending")),
            result=data.get("result"),
            error=data.get("error"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            retries=data.get("retries", 0),
            max_retries=data.get("max_retries", 2),
        )


@dataclass
class TaskGraph:
    """Full task decomposition with execution tracking."""
    root_task: str
    subtasks: dict[str, SubTask] = field(default_factory=dict)
    execution_order: list[list[str]] = field(default_factory=list)  # Parallel batches
    current_batch: int = 0
    created_at: float = field(default_factory=time.time)
    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def add_subtask(self, subtask: SubTask):
        """Add a subtask to the graph."""
        self.subtasks[subtask.id] = subtask
        self._recompute_execution_order()

    def get_subtask(self, task_id: str) -> SubTask | None:
        """Get a subtask by ID."""
        return self.subtasks.get(task_id)

    def get_ready_tasks(self) -> list[SubTask]:
        """Return tasks whose dependencies are all completed."""
        ready = []
        for task in self.subtasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            deps_ok = all(
                self.subtasks[dep].status == TaskStatus.COMPLETED
                for dep in task.depends_on
            )
            deps_failed = any(
                self.subtasks[dep].status in (TaskStatus.FAILED, TaskStatus.BLOCKED)
                for dep in task.depends_on
            )
            if deps_failed:
                task.status = TaskStatus.BLOCKED
            elif deps_ok:
                ready.append(task)
        return ready

    def get_progress(self) -> dict:
        """Get progress information for the task graph."""
        total = len(self.subtasks)
        if total == 0:
            return {"percent": 0, "completed": 0, "total": 0, "pending": 0, "failed": 0, "blocked": 0}

        completed = sum(1 for t in self.subtasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.subtasks.values() if t.status == TaskStatus.FAILED)
        blocked = sum(1 for t in self.subtasks.values() if t.status == TaskStatus.BLOCKED)
        in_progress = sum(1 for t in self.subtasks.values() if t.status == TaskStatus.IN_PROGRESS)
        pending = sum(1 for t in self.subtasks.values() if t.status == TaskStatus.PENDING)

        return {
            "percent": (completed / total) * 100,
            "completed": completed,
            "total": total,
            "pending": pending,
            "failed": failed,
            "blocked": blocked,
            "in_progress": in_progress,
        }

    def _recompute_execution_order(self) -> list[list[str]]:
        """Compute parallel execution batches via topological sort (Kahn's algorithm)."""
        in_degree = {tid: 0 for tid in self.subtasks}
        dependents = {tid: [] for tid in self.subtasks}

        for tid, task in self.subtasks.items():
            for dep in task.depends_on:
                if dep in dependents:
                    dependents[dep].append(tid)
                    in_degree[tid] += 1

        batches = []
        queue = [tid for tid, deg in in_degree.items() if deg == 0]

        while queue:
            batches.append(queue[:])
            next_queue = []
            for tid in queue:
                for dependent in dependents[tid]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_queue.append(dependent)
            queue = next_queue

        self.execution_order = batches
        return batches

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "root_task": self.root_task,
            "subtasks": {tid: t.to_dict() for tid, t in self.subtasks.items()},
            "execution_order": self.execution_order,
            "current_batch": self.current_batch,
            "plan_id": self.plan_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskGraph":
        """Create from dictionary."""
        graph = cls(
            root_task=data["root_task"],
            execution_order=data.get("execution_order", []),
            current_batch=data.get("current_batch", 0),
            plan_id=data.get("plan_id"),
            created_at=data.get("created_at", time.time()),
        )
        for tid, task_data in data.get("subtasks", {}).items():
            graph.subtasks[tid] = SubTask.from_dict(task_data)
        return graph


class TaskDecomposer:
    """LLM-powered task decomposition."""

    def __init__(self, router=None):
        self.router = router

    def set_router(self, router):
        """Set the model router for decomposition."""
        self.router = router

    async def decompose(self, task: str, subtasks: list[dict] = None) -> TaskGraph:
        """Decompose a complex task into a DAG of subtasks."""
        if subtasks:
            return self._build_graph_from_subtasks(task, subtasks)
        return await self._llm_decompose(task)

    def _build_graph_from_subtasks(self, root_task: str, subtasks: list[dict]) -> TaskGraph:
        """Build TaskGraph from provided subtask list."""
        graph = TaskGraph(root_task=root_task)
        for st in subtasks:
            graph.add_subtask(SubTask(
                id=st["id"],
                description=st["description"],
                assigned_agent=st.get("agent"),
                depends_on=st.get("depends_on", []),
            ))
        return graph

    async def _llm_decompose(self, task: str) -> TaskGraph:
        """Use LLM to decompose task into subtasks."""
        if not self.router:
            raise RuntimeError("Router not set for TaskDecomposer")

        prompt = f"""Decompose this complex task into independent subtasks with dependencies:

Task: {task}

Return a JSON array of subtasks in this format:
[
  {{"id": "a", "description": "...", "depends_on": []}},
  {{"id": "b", "description": "...", "depends_on": ["a"]}},
  ...
]

Guidelines:
- Break into 3-8 subtasks
- Each subtask should be independently executable
- Specify dependencies clearly
- Order tasks logically (prerequisites first)"""

        try:
            response = await self.router.send(prompt)
            import json
            import re

            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                subtasks_data = json.loads(json_match.group())
                return self._build_graph_from_subtasks(task, subtasks_data)
            else:
                logger.warning("LLM did not return valid JSON, creating single task")
                graph = TaskGraph(root_task=task)
                graph.add_subtask(SubTask(id="main", description=task))
                return graph

        except Exception as e:
            logger.error(f"Task decomposition failed: {e}")
            graph = TaskGraph(root_task=task)
            graph.add_subtask(SubTask(id="main", description=task))
            return graph

    def compute_execution_order(self, graph: TaskGraph) -> list[list[str]]:
        """Compute parallel execution batches via topological sort."""
        return graph._recompute_execution_order()


class TaskExecutor:
    """Execute tasks from a TaskGraph with progress tracking."""

    def __init__(self, graph: TaskGraph, execute_callback=None):
        self.graph = graph
        self.execute_callback = execute_callback

    async def execute_all(self, max_parallel: int = 4) -> dict[str, Any]:
        """Execute all tasks in the graph, respecting dependencies."""
        results = {}

        while True:
            ready = self.graph.get_ready_tasks()
            if not ready:
                progress = self.graph.get_progress()
                if progress["completed"] + progress["failed"] + progress["blocked"] == progress["total"]:
                    break
                if not any(t.status == TaskStatus.IN_PROGRESS for t in self.graph.subtasks.values()):
                    logger.warning("Task graph deadlock - no ready tasks but incomplete")
                    break
                await asyncio.sleep(0.1)
                continue

            batch = ready[:max_parallel]
            for task in batch:
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = time.time()

            batch_tasks = []
            for task in batch:
                if self.execute_callback:
                    batch_tasks.append(self._execute_single(task))
                else:
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = time.time()
                    task.result = None

            if batch_tasks:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                for task, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        task.status = TaskStatus.FAILED
                        task.error = str(result)
                        task.completed_at = time.time()
                        if task.retries < task.max_retries:
                            task.retries += 1
                            task.status = TaskStatus.PENDING
                            task.error = None
                    else:
                        task.status = TaskStatus.COMPLETED
                        task.result = result
                        task.completed_at = time.time()

                    results[task.id] = task.result

        return results

    async def _execute_single(self, task: SubTask) -> Any:
        """Execute a single subtask with retry logic."""
        try:
            result = await self.execute_callback(task)
            return result
        except Exception as e:
            raise e


# Module-level registry for task graphs
_task_graphs: dict[str, TaskGraph] = {}


def register_graph(graph: TaskGraph) -> str:
    """Register a task graph and return its plan_id."""
    _task_graphs[graph.plan_id] = graph
    return graph.plan_id


def get_graph(plan_id: str) -> TaskGraph | None:
    """Get a task graph by plan_id."""
    return _task_graphs.get(plan_id)


def get_graph_progress(plan_id: str) -> dict | None:
    """Get progress for a task graph."""
    graph = get_graph(plan_id)
    if graph:
        return graph.get_progress()
    return None


def list_graphs() -> list[str]:
    """List all registered plan IDs."""
    return list(_task_graphs.keys())


def cleanup_graph(plan_id: str):
    """Remove a task graph from registry."""
    _task_graphs.pop(plan_id, None)
