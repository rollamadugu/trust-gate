"""A STRONG suite: checks real values across branches.

Run:  trust-gate pricing.py -c "pytest test_pricing_strong.py -q"
Expect: a HIGH mutation score (most faults caught).
"""
from pricing import final_price


def test_no_member_no_bulk():
    assert final_price(50, False) == 50.0


def test_member_discount():
    assert final_price(50, True) == 40.0


def test_bulk_discount_only():
    assert final_price(200, False) == 180.0


def test_member_and_bulk():
    # 200 * 0.8 = 160, 160 > 100 so * 0.9 = 144.0
    assert final_price(200, True) == 144.0


def test_boundary_not_above_100():
    assert final_price(125, True) == 100.0  # 125*0.8 = 100, not > 100
