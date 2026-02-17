from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(slots=True)
class CompilationOutput:
    patterns: dict[str, int]
    rules: list[tuple[str, str]]


def one_pass_compile(lines: list[str]) -> CompilationOutput:
    """One-pass structural extraction from plain text examples."""
    tokens = Counter()
    rules: list[tuple[str, str]] = []
    for line in lines:
        stripped = line.strip().lower()
        if not stripped:
            continue
        for word in stripped.split():
            tokens[word] += 1
        if "if" in stripped and "then" in stripped:
            left, right = stripped.split("then", 1)
            rules.append((left.replace("if", "").strip(), right.strip()))
    return CompilationOutput(patterns=dict(tokens), rules=rules)
