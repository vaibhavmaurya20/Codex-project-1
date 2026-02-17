# Codex-project-1

Reference implementation for **ASCEND-NET Ω X**, a low-resource meta-cognitive execution architecture.

## What is included

- Persistent world state graph (disk-backed JSON).
- Meta-cognitive kernel with dependency-aware scheduling.
- Resource governor for low-memory operation.
- Rule engine + verification fabric (global + task-specific checks).
- One-pass knowledge compiler utility.
- CLI for demo execution, compilation, and state inspection.

## Quick start

```bash
PYTHONPATH=src python -m ascend_net.cli demo --state-dir .ascend_state_demo
PYTHONPATH=src python -m ascend_net.cli status --state-dir .ascend_state_demo
```

## Run tests

```bash
PYTHONPATH=src python -m pytest -q
```

## Docs

Architecture details: `docs/ASCEND_NET_OMEGA_X.md`
