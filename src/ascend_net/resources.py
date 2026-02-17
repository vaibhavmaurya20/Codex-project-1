from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ResourceBudget:
    ram_mb: int
    cpu_percent: int
    io_tokens: int


class ResourceGovernor:
    """Advisory governor that decides whether new agents may be scheduled."""

    def __init__(self, budget: ResourceBudget) -> None:
        self.budget = budget
        self.active_ram_mb = 0
        self.active_agents = 0

    def can_schedule(self, est_ram_mb: int) -> bool:
        return self.active_ram_mb + est_ram_mb <= self.budget.ram_mb

    def allocate(self, est_ram_mb: int) -> bool:
        if not self.can_schedule(est_ram_mb):
            return False
        self.active_ram_mb += est_ram_mb
        self.active_agents += 1
        return True

    def release(self, est_ram_mb: int) -> None:
        self.active_ram_mb = max(0, self.active_ram_mb - est_ram_mb)
        self.active_agents = max(0, self.active_agents - 1)

    def snapshot(self) -> dict[str, int]:
        return {
            "active_ram_mb": self.active_ram_mb,
            "active_agents": self.active_agents,
            "ram_budget_mb": self.budget.ram_mb,
        }
