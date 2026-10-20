"""A tiny example module with branches, to demo trust-gate."""


def final_price(amount: float, is_member: bool) -> float:
    """20% off for members, plus a further 10% off above 100."""
    price = amount
    if is_member:
        price = price * 0.8
    if price > 100:
        price = price * 0.9
    return round(float(price), 2)
