"""Run the gate: apply each mutant, run the test command, score the suite."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

from .mutators import generate_mutants


@dataclass
class GateResult:
    target: str
    total: int
    killed: int
    survived: List[str] = field(default_factory=list)
    errored: int = 0

    @property
    def score(self) -> float:
        return self.killed / self.total if self.total else 1.0

    def passed(self, min_score: float) -> bool:
        return self.score >= min_score


def _run_tests(test_command: str, cwd: Optional[str], timeout: int) -> int:
    """Return the test command's exit code. A timeout counts as 'killed'
    (the mutant changed behaviour enough to hang), signalled by code 124."""
    try:
        proc = subprocess.run(
            test_command, shell=True, cwd=cwd,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
        return proc.returncode
    except subprocess.TimeoutExpired:
        return 124


def run_gate(
    target_file: str,
    test_command: str = "pytest -q",
    min_score: float = 0.8,
    cwd: Optional[str] = None,
    timeout: int = 120,
    limit: Optional[int] = None,
    on_progress=None,
) -> GateResult:
    """Mutate ``target_file`` one fault at a time, run ``test_command`` for each,
    and measure how many faults the suite catches.

    The file is restored to its original contents in all cases.
    """
    with open(target_file, encoding="utf-8") as f:
        original = f.read()

    mutants = generate_mutants(original)
    if limit is not None:
        mutants = mutants[:limit]

    result = GateResult(target=target_file, total=len(mutants), killed=0)
    if not mutants:
        return result

    run_cwd = cwd if cwd is not None else (os.path.dirname(os.path.abspath(target_file)) or ".")
    try:
        for idx, (mutant_src, desc) in enumerate(mutants, start=1):
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(mutant_src)
            rc = _run_tests(test_command, run_cwd, timeout)
            if rc != 0:
                result.killed += 1
            else:
                result.survived.append(desc)
            if on_progress:
                on_progress(idx, result.total, desc, rc)
    finally:
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(original)

    return result
