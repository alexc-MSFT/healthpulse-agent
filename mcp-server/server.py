import json
import random
import uvicorn
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from starlette.types import ASGIApp, Receive, Scope, Send


class EnsureHeadersMiddleware:
    """Inject required headers that some MCP clients (e.g. Copilot Studio) may omit."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http" and scope["method"] == "POST":
            headers = dict(scope["headers"])
            if b"content-type" not in headers:
                headers[b"content-type"] = b"application/json"
            if b"accept" not in headers or b"text/event-stream" not in headers.get(b"accept", b""):
                headers[b"accept"] = b"application/json, text/event-stream"
            scope["headers"] = list(headers.items())
        await self.app(scope, receive, send)


mcp = FastMCP(
    "HealthPulse Server",
    stateless_http=True,
    json_response=True,
)

# ─── Fictional Data ────────────────────────────────────────────────

REGIONS = [
    "London",
    "South East",
    "South West",
    "East of England",
    "Midlands",
    "North West",
    "North East & Yorkshire",
]

TRUSTS: dict[str, list[str]] = {
    "London": ["Royal London Hospital", "St Thomas' Hospital", "King's College Hospital", "University College Hospital"],
    "South East": ["John Radcliffe Hospital", "Southampton General", "Royal Surrey Hospital"],
    "South West": ["Bristol Royal Infirmary", "Royal Devon & Exeter", "Derriford Hospital"],
    "East of England": ["Addenbrooke's Hospital", "Norfolk & Norwich", "Ipswich Hospital"],
    "Midlands": ["Queen Elizabeth Hospital Birmingham", "University Hospital Coventry", "Royal Stoke"],
    "North West": ["Manchester Royal Infirmary", "Royal Liverpool Hospital", "Wythenshawe Hospital"],
    "North East & Yorkshire": ["Leeds General Infirmary", "Newcastle RVI", "Sheffield Teaching Hospital"],
}


def get_regions(region: str = "") -> list[str]:
    if region:
        match = [r for r in REGIONS if region.lower() in r.lower()]
        return match if match else REGIONS
    return REGIONS


def get_date_range(period: str) -> list[str]:
    now = datetime.now()
    if period == "daily":
        return [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    elif period == "weekly":
        return [(now - timedelta(weeks=i)).strftime("%Y-%m-%d") for i in range(7, -1, -1)]
    else:  # monthly
        return [(now - timedelta(days=30 * i)).strftime("%Y-%m-%d") for i in range(5, -1, -1)]


# ─── Tools ─────────────────────────────────────────────────────────

@mcp.tool()
def get_ambulance_wait_times(region: str = "", period: str = "weekly") -> dict:
    """Get ambulance response times by category (Category 1-4) for Contoso Health regions. Returns average response times in minutes over a specified period. Valid periods: daily, weekly, monthly."""
    regions = get_regions(region)
    dates = get_date_range(period)
    data = []
    for date in dates:
        for r in regions:
            data.append({
                "date": date,
                "region": r,
                "category1_minutes": round(random.uniform(6.5, 9.2), 1),
                "category2_minutes": round(random.uniform(18, 42), 1),
                "category3_minutes": round(random.uniform(45, 120), 1),
                "category4_minutes": round(random.uniform(90, 240), 1),
                "total_incidents": random.randint(800, 2400),
            })
    return {
        "title": "Ambulance Response Times",
        "description": "Average ambulance response times by category. Category 1: Life-threatening (target 7 min). Category 2: Emergency (target 18 min). Category 3: Urgent (target 120 min). Category 4: Less urgent.",
        "period": period,
        "data": data,
    }


@mcp.tool()
def get_ae_waiting_times(region: str = "", period: str = "weekly") -> dict:
    """Get Accident & Emergency department waiting times and patient throughput statistics. Returns data on 4-hour target performance, median wait times, and patient volumes. Valid periods: daily, weekly, monthly."""
    regions = get_regions(region)
    dates = get_date_range(period)
    data = []
    for date in dates:
        for r in regions:
            attendances = random.randint(5000, 18000)
            data.append({
                "date": date,
                "region": r,
                "median_wait_minutes": round(random.uniform(120, 280), 1),
                "four_hour_target_pct": round(random.uniform(58, 82), 1),
                "twelve_hour_breaches": random.randint(50, 450),
                "total_attendances": attendances,
                "admissions": int(attendances * random.uniform(0.25, 0.35)),
            })
    return {
        "title": "A&E Waiting Times",
        "description": "Accident & Emergency department performance metrics. The Contoso Health target is 95% of patients seen within 4 hours.",
        "period": period,
        "target": "95% within 4 hours",
        "data": data,
    }


@mcp.tool()
def get_bed_occupancy(region: str = "", bed_type: str = "all") -> dict:
    """Get hospital bed occupancy rates across Contoso Health trusts. Returns percentage occupancy, available beds, and critical care utilisation. Valid bed_type: general, critical_care, maternity, all."""
    regions = get_regions(region)
    bed_types = ["general", "critical_care", "maternity"] if bed_type == "all" else [bed_type]
    data = []
    for r in regions:
        trusts = TRUSTS.get(r, ["General Hospital"])
        for trust in trusts:
            for bt in bed_types:
                if bt == "critical_care":
                    total_beds = random.randint(20, 60)
                elif bt == "maternity":
                    total_beds = random.randint(30, 80)
                else:
                    total_beds = random.randint(200, 600)
                occupancy_pct = round(random.uniform(78, 98), 1)
                occupied_beds = int(total_beds * occupancy_pct / 100)
                data.append({
                    "region": r,
                    "trust": trust,
                    "bed_type": bt,
                    "total_beds": total_beds,
                    "occupied_beds": occupied_beds,
                    "occupancy_pct": occupancy_pct,
                    "available_beds": total_beds - occupied_beds,
                })
    return {
        "title": "Bed Occupancy Rates",
        "description": "Current hospital bed occupancy across Contoso Health trusts. Recommended occupancy is below 85% for safe operation.",
        "snapshot_date": datetime.now().strftime("%Y-%m-%d"),
        "data": data,
    }


@mcp.tool()
def get_regional_health_summary(region: str) -> dict:
    """Get a comprehensive health performance summary for a specific Contoso Health region, including ambulance times, A&E performance, bed occupancy, and trend indicators. Ideal for generating dashboard charts."""
    resolved = get_regions(region)
    region_name = resolved[0] if resolved else region

    trends = ["improving", "stable", "worsening"]
    weekly_trend = []
    now = datetime.now()
    for i in range(7, -1, -1):
        d = now - timedelta(weeks=i)
        weekly_trend.append({
            "week": d.strftime("%Y-%m-%d"),
            "ambulance_cat1": round(random.uniform(6.8, 8.5), 1),
            "ae_4hr_pct": round(random.uniform(60, 78), 1),
            "bed_occupancy_pct": round(random.uniform(82, 96), 1),
        })

    return {
        "title": f"Regional Health Summary: {region_name}",
        "description": "Comprehensive health performance summary including ambulance response, A&E performance, bed occupancy, and 8-week trend data suitable for chart generation.",
        "data": {
            "region": region_name,
            "report_date": now.strftime("%Y-%m-%d"),
            "ambulance": {
                "avg_category1_minutes": round(random.uniform(7.0, 8.8), 1),
                "avg_category2_minutes": round(random.uniform(22, 38), 1),
                "trend": random.choice(trends),
                "incidents_last_week": random.randint(3000, 8000),
            },
            "ae": {
                "four_hour_performance_pct": round(random.uniform(62, 76), 1),
                "median_wait_minutes": round(random.uniform(140, 260), 1),
                "trend": random.choice(trends),
                "weekly_attendances": random.randint(15000, 45000),
            },
            "beds": {
                "overall_occupancy_pct": round(random.uniform(85, 95), 1),
                "critical_care_occupancy_pct": round(random.uniform(78, 96), 1),
                "available_general_beds": random.randint(50, 300),
                "trend": random.choice(trends),
            },
            "weekly_trend_data": weekly_trend,
        },
    }


if __name__ == "__main__":
    app = mcp.streamable_http_app()
    app = EnsureHeadersMiddleware(app)
    uvicorn.run(app, host="0.0.0.0", port=3001)
