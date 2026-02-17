from ascend_net.kernel import MetaCognitiveKernel
from ascend_net.models import TaskNode, TaskStatus, VerificationRule
from ascend_net.resources import ResourceBudget, ResourceGovernor
from ascend_net.rules import Rule, RuleEngine
from ascend_net.verification import VerificationFabric
from ascend_net.wsg import WorldStateGraph


def make_kernel(tmp_path, ram_mb=2048):
    wsg = WorldStateGraph(tmp_path)
    rules = RuleEngine()
    rules.register(Rule("api-tests", "api_endpoint", "unit_test"))
    return MetaCognitiveKernel(
        wsg,
        ResourceGovernor(ResourceBudget(ram_mb, 80, 1000)),
        VerificationFabric(rules),
    )


def test_kernel_executes_dependencies(tmp_path):
    kernel = make_kernel(tmp_path)
    kernel.submit(TaskNode(task_id="T1", title="Build API endpoint", constraints=["must_include_tests"]))
    kernel.submit(TaskNode(task_id="T2", title="Integrate service", dependencies=["T1"]))

    result = kernel.run()

    assert result["T1"] == "verified"
    assert result["T2"] == "verified"


def test_kernel_blocks_when_budget_is_too_low(tmp_path):
    kernel = make_kernel(tmp_path, ram_mb=128)
    kernel.submit(TaskNode(task_id="T1", title="Any task"))

    result = kernel.run()

    assert "insufficient memory budget" in result["T1"]


def test_task_specific_verification_rule_is_applied(tmp_path):
    wsg = WorldStateGraph(tmp_path)
    verifier = VerificationFabric(RuleEngine())
    kernel = MetaCognitiveKernel(
        wsg,
        ResourceGovernor(ResourceBudget(2048, 80, 1000)),
        verifier,
    )
    kernel.submit(
        TaskNode(
            task_id="T1",
            title="Build API endpoint",
            verification_rules=[
                VerificationRule(
                    "api-needs-integration",
                    "API endpoint requires integration plan",
                    trigger_artifact="api_endpoint",
                    required_artifact="integration_plan",
                )
            ],
        )
    )

    result = kernel.run()
    saved = wsg.get_task("T1")

    assert "api-needs-integration" in result["T1"]
    assert saved is not None and saved.status == TaskStatus.FAILED


def test_unknown_dependencies_fail_task(tmp_path):
    kernel = make_kernel(tmp_path)
    kernel.submit(TaskNode(task_id="T1", title="Integrate service", dependencies=["MISSING"]))

    result = kernel.run()

    assert "unknown dependencies" in result["T1"]


def test_world_state_reload_preserves_task_status(tmp_path):
    kernel = make_kernel(tmp_path)
    kernel.submit(TaskNode(task_id="T1", title="Build API endpoint", constraints=["must_include_tests"]))
    kernel.run()

    reloaded = WorldStateGraph(tmp_path)
    task = reloaded.get_task("T1")

    assert task is not None
    assert task.status == TaskStatus.VERIFIED
