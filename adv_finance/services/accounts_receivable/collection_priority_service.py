from __future__ import annotations

from decimal import Decimal


def score_collection_case(case, credit_exposure=None) -> dict:
    score = 0
    factors = []
    days = int(case.oldest_overdue_days or 0)
    overdue = Decimal(str(case.overdue_amount or 0))
    broken = int(case.broken_promise_count or 0)
    disputes = int(case.open_dispute_count or 0)
    if days > 90:
        score += 30; factors.append({"factor": "90+ days overdue", "points": 30})
    elif days > 60:
        score += 20; factors.append({"factor": "60+ days overdue", "points": 20})
    elif days > 30:
        score += 10; factors.append({"factor": "30+ days overdue", "points": 10})
    if broken:
        pts = 25 if broken == 1 else 35
        score += pts; factors.append({"factor": "Broken promise", "points": pts})
    if overdue > Decimal("100000"):
        score += 20; factors.append({"factor": "Overdue above 100000", "points": 20})
    elif overdue > Decimal("50000"):
        score += 10; factors.append({"factor": "Overdue above 50000", "points": 10})
    if credit_exposure and Decimal(str(credit_exposure.get("available_credit") or 0)) < 0:
        score += 20; factors.append({"factor": "Exposure above credit limit", "points": 20})
    if disputes:
        score += 5; factors.append({"factor": "Open dispute", "points": 5})
    if score >= 70:
        priority = "Critical"
    elif score >= 50:
        priority = "High"
    elif score >= 25:
        priority = "Normal"
    else:
        priority = "Low"
    risk_level = "High" if score >= 50 else ("Medium" if score >= 25 else "Low")
    return {"score": score, "priority": priority, "risk_level": risk_level, "factors": factors}
