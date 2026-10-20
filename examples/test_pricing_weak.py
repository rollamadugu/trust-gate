"""A WEAK suite: it passes, but barely checks anything.

Run:  trust-gate pricing.py -c "pytest test_pricing_weak.py -q"
Expect: a LOW mutation score with surviving faults.
"""
from pricing import final_price


def test_returns_a_number():
    assert isinstance(final_price(50, False), float)


def test_runs_for_members():
    final_price(200, True)  # no assertion on the value!
