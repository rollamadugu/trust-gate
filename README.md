# trust-gate

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-standard--library-success)
![License](https://img.shields.io/badge/license-MIT-green)

> **Your tests are green. But are they strong enough to catch a real bug?**

`trust-gate` injects small faults (mutants) into your code, runs your test
command for each one, and measures how many faults your **passing** tests
actually catch. Green tests that miss injected faults are weak tests —
`trust-gate` makes that measurable and lets you **fail CI** when test strength
drops below a threshold.

It's a focused, zero-dependency mutation-testing gate. Pure Python standard
library. Works with any test runner (pytest, unittest, a shell script — anything
that exits non-zero on failure).

> Part of a broader line of work on **trust in AI-driven testing**
> ([TrustLab](https://github.com/rollamadugu/trustlab)). As AI writes more of our
> tests, "it passed" needs to mean "it would have caught the bug." This gate
> checks exactly that.

## Install

```bash
pip install trust-gate        # from PyPI (coming soon)
# or, from source:
pip install -e ".[dev]"
```

## Use

```bash
trust-gate path/to/module.py --test-command "pytest -q" --min-score 0.8
```

- Injects one fault at a time into `module.py`
- Runs your test command; **non-zero exit = fault caught** (good)
- A fault that survives means your tests passed anyway — a weak spot
- Exits `1` if the mutation score is below `--min-score` (so it gates CI)
- Your file is always restored, even on error

## See it in action

The repo ships a tiny `examples/` module with a **weak** and a **strong** suite.

**Weak suite** (passes, but barely checks values):

```
$ trust-gate examples/pricing.py -c "pytest test_pricing_weak.py -q" --cwd examples
  [1/7] SURVIVED  line 8: 0.8 -> 1.8
  [2/7] SURVIVED  line 8: Mult -> Div
  ...
mutants         : 7
caught (killed) : 0
survived        : 7
mutation score  : 0.00%
gate: FAIL  (score 0.00% vs threshold 80%)
```

**Strong suite** (checks real values across branches):

```
$ trust-gate examples/pricing.py -c "pytest test_pricing_strong.py -q" --cwd examples
mutants         : 7
caught (killed) : 7
survived        : 0
mutation score  : 100.00%
gate: PASS  (score 100.00% vs threshold 80%)
```

Same code, same "all green" — but only one suite would actually catch a bug.

## Options

| Flag | Default | Meaning |
|---|---|---|
| `target` | — | Python file to mutate |
| `-c, --test-command` | `pytest -q` | Command that runs your tests |
| `-m, --min-score` | `0.8` | Minimum mutation score to pass the gate |
| `--cwd` | target's dir | Directory to run the test command in |
| `--timeout` | `120` | Per-mutant test timeout (seconds); a hang counts as caught |
| `--limit` | all | Only evaluate the first N mutants (quick check) |
| `-q, --quiet` | off | Only print the summary |

## Mutation operators

Arithmetic (`+ - * / % ** //`), relational (`< > <= >= == !=`), logical
(`and`/`or`), `not` removal, and numeric/boolean constant tweaks. Each eligible
site produces exactly one isolated mutant, so results are deterministic and
every survivor points at a specific line.

## Use in CI (GitHub Actions)

```yaml
- run: pip install trust-gate
- run: trust-gate src/your_module.py -c "pytest -q" --min-score 0.75
```

The step fails the build if your passing tests are too weak.

## How it compares

`trust-gate` is intentionally small and runner-agnostic — a quick, embeddable
*gate*. For large-scale, highly optimised mutation testing, see
[mutmut](https://github.com/boxed/mutmut), [Cosmic Ray](https://github.com/sixty-north/cosmic-ray),
or [PIT](https://pitest.org/) (JVM).

## License

MIT — see [LICENSE](LICENSE).

## Author

**Krishnasai Rollamadugu** — Test Automation Architect, researching trust in
AI-driven software testing. ORCID: 0009-0001-9992-8997
