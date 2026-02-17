from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    BLOCKED = "blocked"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass(slots=True)
class VerificationRule:
    name: str
    description: str
    trigger_artifact: str | None = None
    required_artifact: str | None = None


@dataclass(slots=True)
class TaskNode:
    task_id: str
    title: str
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    verification_rules: list[VerificationRule] = field(default_factory=list)
    confidence_score: float = 0.5
    status: TaskStatus = TaskStatus.PENDING

    def is_ready(self, completed: set[str]) -> bool:
        return all(dep in completed for dep in self.dependencies)
