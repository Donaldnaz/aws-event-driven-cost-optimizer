from unittest.mock import patch

from recommendations import get_all_region_recommendations


@patch("recommendations.get_recommendations")
@patch("recommendations.get_enabled_regions")
def test_get_all_region_recommendations_merges_findings(
    mock_get_regions, mock_get_recommendations
):
    mock_get_regions.return_value = ["us-east-1", "eu-west-1"]
    mock_get_recommendations.side_effect = [
        [
            {
                "category": "unattached_ebs",
                "region": "us-east-1",
                "estimated_monthly_savings": 5.0,
            }
        ],
        [
            {
                "category": "unused_eip",
                "region": "eu-west-1",
                "estimated_monthly_savings": 10.0,
            }
        ],
    ]

    findings, region_errors = get_all_region_recommendations(90, 7)

    assert len(findings) == 2
    assert findings[0]["region"] == "eu-west-1"
    assert findings[0]["estimated_monthly_savings"] == 10.0
    assert region_errors == {}
    assert mock_get_recommendations.call_count == 2


@patch("recommendations.get_recommendations")
@patch("recommendations.get_enabled_regions")
def test_get_all_region_recommendations_isolates_region_errors(
    mock_get_regions, mock_get_recommendations
):
    mock_get_regions.return_value = ["us-east-1", "eu-west-1"]

    def side_effect(region, snapshot_age_days, stopped_instance_days):
        if region == "eu-west-1":
            raise RuntimeError("access denied")
        return [
            {
                "category": "unused_eip",
                "region": "us-east-1",
                "estimated_monthly_savings": 3.6,
            }
        ]

    mock_get_recommendations.side_effect = side_effect

    findings, region_errors = get_all_region_recommendations(90, 7)

    assert len(findings) == 1
    assert findings[0]["region"] == "us-east-1"
    assert region_errors == {"eu-west-1": "access denied"}
