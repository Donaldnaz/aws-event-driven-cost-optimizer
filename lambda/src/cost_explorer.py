from datetime import date, timedelta

import boto3


def _parse_amount(result: dict) -> float:
    total = result.get("Total", {})
    unblended = total.get("UnblendedCost", {})
    return float(unblended.get("Amount", 0))


def _parse_daily_series(results: list) -> list:
    series = []
    for row in results:
        period = row.get("TimePeriod", {})
        amount = _parse_amount(row)
        series.append(
            {
                "date": period.get("Start"),
                "amount_usd": round(amount, 2),
            }
        )
    return series


def _parse_by_service(results: list, limit: int = 10) -> list:
    services = []
    for row in results:
        groups = row.get("Groups", [])
        for group in groups:
            service_name = group.get("Keys", ["Unknown"])[0]
            cost = group.get("Metrics", {}).get("UnblendedCost", {})
            services.append(
                {
                    "service": service_name,
                    "amount_usd": round(float(cost.get("Amount", 0)), 2),
                }
            )
    services.sort(key=lambda s: s["amount_usd"], reverse=True)
    return services[:limit]


def _get_cost(
    client,
    start: date,
    end: date,
    granularity: str = "DAILY",
    group_by: list | None = None,
) -> dict:
    params = {
        "TimePeriod": {
            "Start": start.isoformat(),
            "End": end.isoformat(),
        },
        "Granularity": granularity,
        "Metrics": ["UnblendedCost"],
    }
    if group_by:
        params["GroupBy"] = group_by

    return client.get_cost_and_usage(**params)


def get_cost_summary() -> dict:
    client = boto3.client("ce", region_name="us-east-1")
    today = date.today()
    yesterday = today - timedelta(days=1)
    month_start = yesterday.replace(day=1)

    # Cost Explorer end date is exclusive.
    end_exclusive = today

    yesterday_resp = _get_cost(client, yesterday, end_exclusive, granularity="DAILY")
    yesterday_usd = _parse_amount(yesterday_resp["ResultsByTime"][0])

    mtd_resp = _get_cost(client, month_start, end_exclusive, granularity="MONTHLY")
    mtd_usd = _parse_amount(mtd_resp["ResultsByTime"][0])

    last_7_start = yesterday - timedelta(days=6)
    daily_resp = _get_cost(client, last_7_start, end_exclusive, granularity="DAILY")
    daily_series = _parse_daily_series(daily_resp["ResultsByTime"])

    service_resp = _get_cost(
        client,
        last_7_start,
        end_exclusive,
        granularity="MONTHLY",
        group_by=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    top_services = _parse_by_service(service_resp["ResultsByTime"])

    prior_7_end = last_7_start
    prior_7_start = prior_7_end - timedelta(days=7)
    prior_resp = _get_cost(client, prior_7_start, prior_7_end, granularity="MONTHLY")
    prior_total = _parse_amount(prior_resp["ResultsByTime"][0])
    current_total = sum(d["amount_usd"] for d in daily_series)

    wow_change_pct = 0.0
    if prior_total > 0:
        wow_change_pct = round(
            ((current_total - prior_total) / prior_total) * 100, 2
        )

    return {
        "mtd_usd": round(mtd_usd, 2),
        "yesterday_usd": round(yesterday_usd, 2),
        "daily_series": daily_series,
        "top_services": top_services,
        "wow_change_pct": wow_change_pct,
    }
