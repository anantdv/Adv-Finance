from __future__ import annotations
from adv_finance.services.intercompany.close_service import get_intercompany_close_readiness

def execute(filters=None):
    r=get_intercompany_close_readiness((filters or {}).get("company"),(filters or {}).get("period_end"))
    return ["Metric:Data:240","Value:Data:140"], [[k.replace("_"," ").title(),v] for k,v in r.items()]
