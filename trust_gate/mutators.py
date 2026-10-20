"""AST-based mutation operators.

Each eligible node in the source produces exactly one mutant (a single,
isolated change), so results are deterministic and easy to report. The same
traversal is used to count sites and to apply a specific mutation, which keeps
the indices aligned between the two passes.
"""
from __future__ import annotations

import ast
from typing import List, Tuple

# Arithmetic operator replacement (AOR)
ARITH = {
    ast.Add: ast.Sub, ast.Sub: ast.Add,
    ast.Mult: ast.Div, ast.Div: ast.Mult,
    ast.Mod: ast.Mult, ast.Pow: ast.Mult, ast.FloorDiv: ast.Div,
}
# Relational operator replacement (ROR)
CMP = {
    ast.Lt: ast.Gt, ast.Gt: ast.Lt,
    ast.LtE: ast.GtE, ast.GtE: ast.LtE,
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
}
# Logical connector replacement (LCR)
BOOL = {ast.And: ast.Or, ast.Or: ast.And}


class _Mutator(ast.NodeTransformer):
    """Mutates the ``target``-th eligible node. Use target=-1 only to count."""

    def __init__(self, target: int):
        self.target = target
        self.index = 0
        self.description = None

    def _hit(self, desc: str, lineno: int) -> bool:
        is_target = self.index == self.target
        if is_target:
            self.description = f"line {lineno}: {desc}"
        self.index += 1
        return is_target

    def visit_BinOp(self, node):
        self.generic_visit(node)
        t = type(node.op)
        if t in ARITH and self._hit(f"{t.__name__} -> {ARITH[t].__name__}", node.lineno):
            node.op = ARITH[t]()
        return node

    def visit_Compare(self, node):
        self.generic_visit(node)
        if len(node.ops) == 1:
            t = type(node.ops[0])
            if t in CMP and self._hit(f"{t.__name__} -> {CMP[t].__name__}", node.lineno):
                node.ops[0] = CMP[t]()
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        t = type(node.op)
        if t in BOOL and self._hit(f"{t.__name__} -> {BOOL[t].__name__}", node.lineno):
            node.op = BOOL[t]()
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Not) and self._hit("not x -> x", node.lineno):
            return node.operand
        return node

    def visit_Constant(self, node):
        self.generic_visit(node)
        v = node.value
        if isinstance(v, bool):
            if self._hit(f"{v} -> {not v}", node.lineno):
                return ast.copy_location(ast.Constant(value=not v), node)
        elif isinstance(v, (int, float)):
            if self._hit(f"{v} -> {v + 1}", node.lineno):
                return ast.copy_location(ast.Constant(value=v + 1), node)
        return node


def count_sites(source: str) -> int:
    """Number of mutable sites in ``source``."""
    m = _Mutator(target=-1)
    m.visit(ast.parse(source))
    return m.index


def generate_mutants(source: str) -> List[Tuple[str, str]]:
    """Return a list of ``(mutant_source, description)`` for ``source``."""
    total = count_sites(source)
    out: List[Tuple[str, str]] = []
    for i in range(total):
        tree = ast.parse(source)
        m = _Mutator(target=i)
        new_tree = m.visit(tree)
        ast.fix_missing_locations(new_tree)
        try:
            mutant_src = ast.unparse(new_tree)
        except Exception:
            continue
        if m.description is None:
            continue
        out.append((mutant_src, m.description))
    return out
