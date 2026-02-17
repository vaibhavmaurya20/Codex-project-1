from __future__ import annotations

import argparse
import json

from .compiler import one_pass_compile
from .kernel import MetaCognitiveKernel
from .models import TaskNode, VerificationRule
from .resources import ResourceBudget, ResourceGovernor
from .rules import Rule, RuleEngine
from .verification import VerificationFabric
from .wsg import WorldStateGraph


def build_demo_kernel(state_dir: str, ram_budget_mb: int = 4096) -> MetaCognitiveKernel:
    wsg = WorldStateGraph(state_dir)
    rules = RuleEngine()
    rules.register(Rule("api-must-have-tests", "api_endpoint", "unit_test"))
    verifier = VerificationFabric(rules)
    governor = ResourceGovernor(ResourceBudget(ram_mb=ram_budget_mb, cpu_percent=80, io_tokens=1000))
    return MetaCognitiveKernel(wsg, governor, verifier)


def cmd_demo(args: argparse.Namespace) -> int:
    kernel = build_demo_kernel(args.state_dir, args.ram_budget_mb)
    kernel.submit(
        TaskNode(
            task_id="T1",
            title="Build API endpoint",
            constraints=["must_include_tests"],
            verification_rules=[
                VerificationRule(
                    "api-must-have-tests",
                    "Require unit_test artifact",
                    trigger_artifact="api_endpoint",
                    required_artifact="unit_test",
                )
            ],
        )
    )
    kernel.submit(TaskNode(task_id="T2", title="Integrate service", dependencies=["T1"]))
    summary = kernel.run()
    for task_id, status in summary.items():
        print(f"{task_id}: {status}")
    print(kernel.world_state.stats())
    return 0


def cmd_compile(args: argparse.Namespace) -> int:
    with open(args.input, "r", encoding="utf-8") as handle:
        content = handle.read().splitlines()
    output = one_pass_compile(content)
    print(f"patterns={len(output.patterns)} rules={len(output.rules)}")
    for condition, required in output.rules[:10]:
        print(f"IF {condition} THEN {required}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    wsg = WorldStateGraph(args.state_dir)
    tasks = sorted(wsg.all_tasks(), key=lambda t: t.task_id)
    payload = {
        "stats": wsg.stats(),
        "tasks": [
            {
                "task_id": t.task_id,
                "status": t.status.value,
                "confidence": t.confidence_score,
                "dependencies": t.dependencies,
            }
            for t in tasks
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ASCEND-NET Ω X runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Run demo task graph")
    demo.add_argument("--state-dir", default=".ascend_state")
    demo.add_argument("--ram-budget-mb", type=int, default=4096)
    demo.set_defaults(func=cmd_demo)

    compile_cmd = sub.add_parser("compile", help="Run one-pass knowledge compilation")
    compile_cmd.add_argument("input")
    compile_cmd.set_defaults(func=cmd_compile)

    status_cmd = sub.add_parser("status", help="Inspect persistent task graph state")
    status_cmd.add_argument("--state-dir", default=".ascend_state")
    status_cmd.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
