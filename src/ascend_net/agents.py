from __future__ import annotations

from dataclasses import dataclass

from .models import TaskNode, TaskStatus


@dataclass(slots=True)
class AgentResult:
    task_id: str
    artifacts: set[str]
    confidence_delta: float


class BaseAgent:
    name = "base"
    est_ram_mb = 256

    def run(self, task: TaskNode) -> AgentResult:
        task.status = TaskStatus.RUNNING
        normalized = task.title.replace(" ", "_").lower()
        artifacts = {f"{normalized}.impl"}
        return AgentResult(task.task_id, artifacts, 0.05)


class CodeAgent(BaseAgent):
    name = "code"
    est_ram_mb = 768

    def run(self, task: TaskNode) -> AgentResult:
        base = super().run(task)
        artifacts = set(base.artifacts)
        title = task.title.lower()

        if "api" in title:
            artifacts.add("api_endpoint")
            artifacts.add("unit_test")
        elif "integrate" in title:
            artifacts.add("integration_plan")
        else:
            artifacts.add("artifact")

        return AgentResult(base.task_id, artifacts, 0.1)
