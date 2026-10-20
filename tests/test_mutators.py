import ast

from trust_gate.mutators import count_sites, generate_mutants


def test_counts_arithmetic_and_comparison_sites():
    src = "def f(a, b):\n    return a + b > 0\n"
    # one BinOp (a + b) + one Compare (> 0) + one Constant (0) = 3 sites
    assert count_sites(src) == 3


def test_every_mutant_is_valid_python_and_differs():
    src = "def f(a, b):\n    return a + b\n"
    mutants = generate_mutants(src)
    assert len(mutants) >= 1
    for mutant_src, desc in mutants:
        ast.parse(mutant_src)          # must be valid Python
        assert mutant_src != src       # must actually change something
        assert desc                    # must describe the change


def test_arithmetic_mutation_changes_operator():
    src = "x = a + b\n"
    mutants = generate_mutants(src)
    sources = [m for m, _ in mutants]
    assert any("a - b" in s for s in sources)


def test_comparison_mutation_flips_operator():
    src = "y = a < b\n"
    mutants = generate_mutants(src)
    sources = [m for m, _ in mutants]
    assert any("a > b" in s for s in sources)


def test_boolean_constant_mutation():
    src = "flag = True\n"
    mutants = generate_mutants(src)
    sources = [m for m, _ in mutants]
    assert any("False" in s for s in sources)


def test_no_sites_returns_empty():
    src = "x = foo(bar)\n"
    assert generate_mutants(src) == []
