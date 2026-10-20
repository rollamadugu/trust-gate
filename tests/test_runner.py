import sys
import textwrap

from trust_gate.runner import run_gate


def _write(p, text):
    p.write_text(textwrap.dedent(text), encoding="utf-8")


def test_strong_tests_catch_faults(tmp_path):
    _write(tmp_path / "m.py", """
        def add(a, b):
            return a + b
    """)
    _write(tmp_path / "check_strong.py", """
        import m
        assert m.add(2, 3) == 5
        assert m.add(10, 5) == 15
        assert m.add(0, 0) == 0
    """)
    res = run_gate(
        target_file=str(tmp_path / "m.py"),
        test_command=f'"{sys.executable}" check_strong.py',
        cwd=str(tmp_path),
        timeout=30,
    )
    assert res.total > 0
    # add -> sub makes add(2,3) == -1, so a strong suite catches it: high score
    assert res.score == 1.0
    assert res.survived == []


def test_weak_tests_let_faults_survive(tmp_path):
    _write(tmp_path / "m.py", """
        def add(a, b):
            return a + b
    """)
    # weak: only checks the type, not the value -> add->sub still returns an int
    _write(tmp_path / "check_weak.py", """
        import m
        assert isinstance(m.add(2, 3), int)
    """)
    res = run_gate(
        target_file=str(tmp_path / "m.py"),
        test_command=f'"{sys.executable}" check_weak.py',
        cwd=str(tmp_path),
        timeout=30,
    )
    assert res.total > 0
    assert res.survived, "a value-blind test should let the arithmetic mutant survive"
    assert res.score < 1.0


def test_target_file_is_restored(tmp_path):
    original = "def add(a, b):\n    return a + b\n"
    (tmp_path / "m.py").write_text(original, encoding="utf-8")
    _write(tmp_path / "check.py", """
        import m
        assert m.add(1, 1) == 2
    """)
    run_gate(
        target_file=str(tmp_path / "m.py"),
        test_command=f'"{sys.executable}" check.py',
        cwd=str(tmp_path),
        timeout=30,
    )
    assert (tmp_path / "m.py").read_text(encoding="utf-8") == original
