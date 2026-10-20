"""Command-line interface for trust-gate."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .runner import run_gate


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trust-gate",
        description="Mutation-based test-strength gate. Injects faults into your "
                    "code, runs your tests, and reports how many faults your "
                    "passing tests actually catch.",
    )
    p.add_argument("target", help="Path to the Python file to mutate.")
    p.add_argument("-c", "--test-command", default="pytest -q",
                   help='Command that runs your tests (default: "pytest -q"). '
                        "Non-zero exit = tests failed = fault caught.")
    p.add_argument("-m", "--min-score", type=float, default=0.8,
                   help="Minimum mutation score to pass the gate (default: 0.8).")
    p.add_argument("--cwd", default=None,
                   help="Directory to run the test command in "
                        "(default: the target file's directory).")
    p.add_argument("--timeout", type=int, default=120,
                   help="Per-mutant test timeout in seconds (default: 120).")
    p.add_argument("--limit", type=int, default=None,
                   help="Only evaluate the first N mutants (useful for a quick check).")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Only print the summary line.")
    p.add_argument("-v", "--version", action="version",
                   version=f"trust-gate {__version__}")
    return p


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)

    def progress(i, total, desc, rc):
        if not args.quiet:
            mark = "killed " if rc != 0 else "SURVIVED"
            print(f"  [{i}/{total}] {mark}  {desc}")

    if not args.quiet:
        print(f"trust-gate {__version__} - mutating {args.target}")
        print(f"test command: {args.test_command}\n")

    result = run_gate(
        target_file=args.target,
        test_command=args.test_command,
        min_score=args.min_score,
        cwd=args.cwd,
        timeout=args.timeout,
        limit=args.limit,
        on_progress=progress,
    )

    if result.total == 0:
        print("No mutable sites found in target. Nothing to gate.")
        return 0

    passed = result.passed(args.min_score)
    print("\n" + "-" * 48)
    print(f"target          : {result.target}")
    print(f"mutants         : {result.total}")
    print(f"caught (killed) : {result.killed}")
    print(f"survived        : {len(result.survived)}")
    print(f"mutation score  : {result.score:.2%}")
    if result.survived and not args.quiet:
        print("\nweak spots (faults your tests did NOT catch):")
        for s in result.survived:
            print(f"  - {s}")
    print("-" * 48)
    verdict = "PASS" if passed else "FAIL"
    print(f"gate: {verdict}  (score {result.score:.2%} vs threshold {args.min_score:.0%})")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
