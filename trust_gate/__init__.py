"""trust-gate: a mutation-based test-strength gate.

Injects small faults (mutants) into your code, runs your test command, and
reports how many faults your passing tests actually catch. Green tests that
miss injected faults are weak tests -- trust-gate makes that measurable and
gateable in CI.
"""
from .mutators import generate_mutants
from .runner import run_gate, GateResult

__version__ = "0.1.0"
__all__ = ["generate_mutants", "run_gate", "GateResult", "__version__"]
