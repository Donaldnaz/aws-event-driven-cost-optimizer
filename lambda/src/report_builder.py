import uuid
from datetime import datetime, timezone


def build_report(
    account_id: str,
    cost_summary: dict,
    recommendations: list,
    errors: list,
    generated_at: datetime | None = None,
    regions_scanned: list[str] | None = None,
) -> dict:
    generated_at = generated_at or datetime.now(timezone.utc)
    total_savings = sum(
        r.get("estimated_monthly_savings", 0) for r in recommendations
    )

    report = {
        "report_id": str(uuid.uuid4()),
        "generated_at": generated_at.isoformat(),
        "account_id": account_id,
        "cost_summary": cost_summary,
        "recommendations": recommendations,
        "totals": {
            "finding_count": len(recommendations),
            "estimated_monthly_savings_usd": round(total_savings, 2),
        },
        "errors": errors,
    }

    if regions_scanned is not None:
        report["regions_scanned"] = regions_scanned
        report["totals"]["regions_scanned_count"] = len(regions_scanned)

    return report
