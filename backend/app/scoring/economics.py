from __future__ import annotations


def compute_reverse_unit_economics(
    retail_price: float,
    desired_margin_pct: float = 0.30,
    tax_withholding_pct: float = 0.09,
) -> dict:
    """
    Computes Reverse Unit Economics (Target Purchase Price):
    - retail_price: Current market retail price on Mercado Libre (MXN).
    - ml_fee: Marketplace fee (~17.5% average) + fixed fee ($25 MXN for items under $299 MXN).
    - shipping: Free shipping threshold in Mexico starts at $299 MXN ($85 MXN average cost to seller).
    - taxes: Standard Mexican tax withholdings for digital platforms (8% IVA + 1% ISR = 9%).
    - target_profit: Desired clean profit in pesos (e.g., 30% of retail price).
    - max_supplier_cost: The ABSOLUTE MAXIMUM price you can pay the supplier/artisan/factory.
      If supplier charges more than this, your net margin drops below the target.
    """
    if retail_price <= 0:
        return {
            "retail_price": 0.0,
            "ml_fee": 0.0,
            "shipping": 0.0,
            "taxes": 0.0,
            "target_profit": 0.0,
            "max_supplier_cost": 0.0,
            "target_margin_pct": desired_margin_pct * 100,
        }

    ml_fee = round(retail_price * 0.175 + (0.0 if retail_price >= 299 else 25.0), 2)
    shipping = 85.0 if retail_price >= 299 else 0.0
    taxes = round(retail_price * tax_withholding_pct, 2)
    target_profit = round(retail_price * desired_margin_pct, 2)

    max_cost = max(0.0, retail_price - ml_fee - shipping - taxes - target_profit)

    return {
        "retail_price": round(retail_price, 2),
        "ml_fee": ml_fee,
        "shipping": shipping,
        "taxes": taxes,
        "target_profit": target_profit,
        "max_supplier_cost": round(max_cost, 2),
        "target_margin_pct": round(desired_margin_pct * 100, 1),
    }
