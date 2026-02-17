from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import TaskNode, TaskStatus, VerificationRule


class WorldStateGraph:
    """Disk-backed, JSON-indexed world state graph for task memory."""

    def __init__(self, root: str | Path = ".ascend_state") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.tasks_path = self.root / "tasks.json"
        self.rules_path = self.root / "rules.json"
        self._tasks: dict[str, TaskNode] = {}
        self._rules: dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if self.tasks_path.exists():
            raw = json.loads(self.tasks_path.read_text())
            for key, task in raw.items():
                verification_rules = task.get("verification_rules", [])
                task["verification_rules"] = [VerificationRule(**r) for r in verification_rules]
                task["status"] = TaskStatus(task.get("status", TaskStatus.PENDING.value))
                self._tasks[key] = TaskNode(**task)
        if self.rules_path.exists():
            self._rules = json.loads(self.rules_path.read_text())

    def persist(self) -> None:
        serializable = {}
        for task_id, task in self._tasks.items():
            item = asdict(task)
            item["status"] = task.status.value
            serializable[task_id] = item
        self.tasks_path.write_text(json.dumps(serializable, indent=2))
        self.rules_path.write_text(json.dumps(self._rules, indent=2))

    def upsert_task(self, task: TaskNode) -> None:
        self._tasks[task.task_id] = task
        self.persist()

    def get_task(self, task_id: str) -> TaskNode | None:
        return self._tasks.get(task_id)

    def all_tasks(self) -> list[TaskNode]:
        return list(self._tasks.values())

    def add_rule(self, name: str, rule: str) -> None:
        self._rules[name] = rule
        self.persist()

    def all_rules(self) -> dict[str, str]:
        return dict(self._rules)

    def stats(self) -> dict[str, Any]:
        return {
            "tasks": len(self._tasks),
            "rules": len(self._rules),
            "storage": str(self.root.resolve()),
        }
