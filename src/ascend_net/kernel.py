from __future__ import annotations

from collections import deque

from .agents import CodeAgent
from .models import TaskNode, TaskStatus
from .resources import ResourceGovernor
from .verification import VerificationFabric
from .wsg import WorldStateGraph


class MetaCognitiveKernel:
    """Coordinates scheduling, execution, and verification across tasks."""

    def __init__(
        self,
        world_state: WorldStateGraph,
        governor: ResourceGovernor,
        verifier: VerificationFabric,
    ) -> None:
        self.world_state = world_state
        self.governor = governor
        self.verifier = verifier
        self.agent = CodeAgent()

    def submit(self, task: TaskNode) -> None:
        self.world_state.upsert_task(task)

    def run(self) -> dict[str, str]:
        all_tasks = sorted(self.world_state.all_tasks(), key=lambda t: t.task_id)
        known_ids = {task.task_id for task in all_tasks}
        completed: set[str] = {task.task_id for task in all_tasks if task.status == TaskStatus.VERIFIED}
        queue = deque(all_tasks)
        summary: dict[str, str] = {}
        blocked_streak = 0

        while queue:
            task = queue.popleft()

            if task.status == TaskStatus.VERIFIED:
                completed.add(task.task_id)
                blocked_streak = 0
                continue

            unknown_deps = [dep for dep in task.dependencies if dep not in known_ids]
            if unknown_deps:
                task.status = TaskStatus.FAILED
                message = f"failed: unknown dependencies {unknown_deps}"
                summary[task.task_id] = message
                task.outputs = {"artifacts": [], "verification": [message]}
                self.world_state.upsert_task(task)
                blocked_streak = 0
                continue

            if not task.is_ready(completed):
                task.status = TaskStatus.BLOCKED
                self.world_state.upsert_task(task)
                queue.append(task)
                blocked_streak += 1
                if blocked_streak >= len(queue) + 1:
                    summary[task.task_id] = "blocked: unresolved dependencies (possible cycle)"
                    break
                continue

            if not self.governor.allocate(self.agent.est_ram_mb):
                task.status = TaskStatus.BLOCKED
                summary[task.task_id] = "blocked: insufficient memory budget"
                task.outputs = {"artifacts": [], "verification": [summary[task.task_id]]}
                self.world_state.upsert_task(task)
                blocked_streak = 0
                continue

            result = self.agent.run(task)
            verification = self.verifier.verify(task, result.artifacts)
            task.confidence_score = min(1.0, task.confidence_score + result.confidence_delta)
            if verification.passed:
                task.status = TaskStatus.VERIFIED
                summary[task.task_id] = "verified"
                completed.add(task.task_id)
            else:
                task.status = TaskStatus.FAILED
                summary[task.task_id] = "; ".join(verification.findings)
            task.outputs = {"artifacts": sorted(result.artifacts), "verification": verification.findings}
            self.world_state.upsert_task(task)
            self.governor.release(self.agent.est_ram_mb)
            blocked_streak = 0

        return summary
