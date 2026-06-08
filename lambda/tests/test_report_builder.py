from datetime import datetime, timezone

from report_builder import build_report


def test_build_report_computes_totals():
    recommendations = [
        {"category": "unattached_ebs", "estimated_monthly_savings": 10.0},
        {"category": "unused_eip", "estimated_monthly_savings": 3.6},
    ]
    cost_summary = {
        "mtd_usd": 150.0,
        "yesterday_usd": 12.5,
        "daily_series": [],
        "top_services": [],
        "wow_change_pct": -5.2,
    }

    report = build_report(
        account_id="123456789012",
        cost_summary=cost_summary,
        recommendations=recommendations,
        errors=[],
        generated_at=datetime(2026, 6, 7, 2, 0, 15, tzinfo=timezone.utc),
    )

    assert report["account_id"] == "123456789012"
    assert report["totals"]["finding_count"] == 2
    assert report["totals"]["estimated_monthly_savings_usd"] == 13.6
    assert report["cost_summary"]["mtd_usd"] == 150.0


def test_build_report_includes_regions_scanned():
    report = build_report(
        account_id="123456789012",
        cost_summary={"mtd_usd": 0, "yesterday_usd": 0, "daily_series": [], "top_services": [], "wow_change_pct": 0},
        recommendations=[],
        errors=[],
        regions_scanned=["us-east-1", "eu-west-1"],
    )

    assert report["regions_scanned"] == ["us-east-1", "eu-west-1"]
    assert report["totals"]["regions_scanned_count"] == 2
