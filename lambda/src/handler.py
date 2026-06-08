import json
import logging
from datetime import datetime, timezone

import boto3

from config import get_config
from cost_explorer import get_cost_summary
from recommendations import get_all_region_recommendations
from regions import get_enabled_regions
from report_builder import build_report

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _build_sns_message(report: dict, s3_uri: str) -> str:
    cost = report["cost_summary"]
    totals = report["totals"]
    lines = [
        "AWS Cost Optimization Report",
        f"Generated: {report['generated_at']}",
        "",
        f"Yesterday spend: ${cost['yesterday_usd']:.2f}",
        f"Month-to-date spend: ${cost['mtd_usd']:.2f}",
        f"Week-over-week change: {cost['wow_change_pct']:.1f}%",
        "",
        f"Findings: {totals['finding_count']}",
        f"Estimated monthly savings: ${totals['estimated_monthly_savings_usd']:.2f}",
        "",
        "Top recommendations:",
    ]

    for rec in report["recommendations"][:5]:
        lines.append(
            f"  - [{rec['severity']}] {rec['category']}: {rec['resource_id']} "
            f"(~${rec['estimated_monthly_savings']:.2f}/mo)"
        )

    if not report["recommendations"]:
        lines.append("  - No optimization opportunities found")

    lines.extend(["", f"Full report: {s3_uri}"])

    if report.get("errors"):
        lines.append("")
        lines.append("Errors during collection:")
        for err in report["errors"]:
            lines.append(f"  - {err}")

    return "\n".join(lines)


def lambda_handler(event, context):
    config = get_config()
    errors = []
    account_id = boto3.client("sts").get_caller_identity()["Account"]

    cost_summary = {}
    try:
        cost_summary = get_cost_summary()
    except Exception as exc:
        logger.exception("Failed to collect cost data")
        errors.append(f"cost_explorer: {exc}")
        cost_summary = {
            "mtd_usd": 0,
            "yesterday_usd": 0,
            "daily_series": [],
            "top_services": [],
            "wow_change_pct": 0,
        }

    recommendations = []
    regions_scanned = []
    try:
        regions_scanned = get_enabled_regions()
        recommendations, region_errors = get_all_region_recommendations(
            snapshot_age_days=config["snapshot_age_days"],
            stopped_instance_days=config["stopped_instance_days"],
        )
        for region, msg in region_errors.items():
            errors.append(f"recommendations/{region}: {msg}")
    except Exception as exc:
        logger.exception("Failed to collect recommendations")
        errors.append(f"recommendations: {exc}")

    report = build_report(
        account_id=account_id,
        cost_summary=cost_summary,
        recommendations=recommendations,
        errors=errors,
        regions_scanned=regions_scanned or None,
    )

    now = datetime.now(timezone.utc)
    s3_key = (
        f"reports/{now.year:04d}/{now.month:02d}/{now.day:02d}/"
        f"cost-report-{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    s3_uri = f"s3://{config['report_bucket']}/{s3_key}"

    s3_client = boto3.client("s3")
    s3_client.put_object(
        Bucket=config["report_bucket"],
        Key=s3_key,
        Body=json.dumps(report, indent=2, default=str),
        ContentType="application/json",
    )
    logger.info("Report uploaded to %s", s3_uri)

    sns_client = boto3.client("sns")
    sns_client.publish(
        TopicArn=config["sns_topic_arn"],
        Subject="AWS Cost Optimization Report",
        Message=_build_sns_message(report, s3_uri),
    )
    logger.info("SNS notification published")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "report_id": report["report_id"],
                "s3_uri": s3_uri,
                "finding_count": report["totals"]["finding_count"],
            }
        ),
    }
