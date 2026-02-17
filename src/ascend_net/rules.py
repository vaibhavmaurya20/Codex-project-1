from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Rule:
    name: str
    condition: str
    required: str


class RuleEngine:
    """Simple deterministic rule checker over produced artifacts."""

    def __init__(self) -> None:
        self._rules: list[Rule] = []

    def register(self, rule: Rule) -> None:
        self._rules.append(rule)

    def validate_artifacts(self, artifacts: set[str], extra_rules: list[Rule] | None = None) -> list[str]:
        active_rules = [*self._rules, *(extra_rules or [])]
        violations: list[str] = []
        for rule in active_rules:
            if rule.condition in artifacts and rule.required not in artifacts:
                violations.append(
                    f"Rule `{rule.name}` violated: `{rule.condition}` requires `{rule.required}`"
                )
        return violations

    def all_rules(self) -> list[Rule]:
        return list(self._rules)
