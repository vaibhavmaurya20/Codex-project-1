from __future__ import annotations

from dataclasses import dataclass

from .models import TaskNode
from .rules import Rule, RuleEngine


@dataclass(slots=True)
class VerificationResult:
    passed: bool
    findings: list[str]


class VerificationFabric:
    """Deterministic verification: global rules + task-specific rules."""

    def __init__(self, rules: RuleEngine) -> None:
        self.rules = rules

    @staticmethod
    def _task_rules(task: TaskNode) -> list[Rule]:
        derived: list[Rule] = []
        for vr in task.verification_rules:
            if vr.trigger_artifact and vr.required_artifact:
                derived.append(Rule(vr.name, vr.trigger_artifact, vr.required_artifact))
        return derived

    def verify(self, task: TaskNode, artifacts: set[str]) -> VerificationResult:
        findings = self.rules.validate_artifacts(artifacts, extra_rules=self._task_rules(task))

        # Constraint aliases for practical policy checks.
        if "must_include_tests" in task.constraints and "unit_test" not in artifacts:
            findings.append("Constraint violated: must_include_tests requires `unit_test`")

        return VerificationResult(passed=not findings, findings=findings)
