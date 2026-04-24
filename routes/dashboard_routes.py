from fastapi import APIRouter
from database.database import lead_collection

router = APIRouter()

@router.get("/dashboard")
def get_dashboard():
    leads = list(lead_collection.find())

    total_leads = len(leads)

    closed_won = [l for l in leads if l.get("status") == "Closed Won"]
    revenue = sum(l.get("totalAmount", 0) for l in closed_won)

    conversion = (len(closed_won) / total_leads * 100) if total_leads else 0

    return {
        "total_leads": total_leads,
        "revenue": revenue,
        "conversion_rate": round(conversion, 2)
    }