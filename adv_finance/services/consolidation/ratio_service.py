from __future__ import annotations

from decimal import Decimal

from adv_finance.services.consolidation.report_service import balance_sheet, profit_loss


def safe_div(num, den):
    den = Decimal(str(den or 0))
    return Decimal("0") if den == 0 else Decimal(str(num or 0)) / den


def group_ratios(period: str) -> dict:
    bs = balance_sheet(period)
    pl = profit_loss(period)
    assets = bs.get("Asset", Decimal("0"))
    liabilities = abs(bs.get("Liability", Decimal("0")))
    equity = abs(bs.get("Equity", Decimal("0")))
    revenue = pl.get("Revenue", Decimal("0"))
    net = pl.get("Net Profit", Decimal("0"))
    return {"Current Ratio": safe_div(assets, liabilities), "Quick Ratio": safe_div(assets, liabilities), "Working Capital": assets - liabilities, "Debt Ratio": safe_div(liabilities, assets), "Debt Equity": safe_div(liabilities, equity), "Gross Margin": safe_div(net, revenue), "Operating Margin": safe_div(pl.get("Operating Profit"), revenue), "Net Margin": safe_div(net, revenue), "ROA": safe_div(net, assets), "ROE": safe_div(net, equity), "Cash Conversion": Decimal("0"), "DSO": Decimal("0"), "DPO": Decimal("0"), "Inventory Days": Decimal("0")}
