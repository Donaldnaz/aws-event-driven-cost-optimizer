from unittest.mock import MagicMock, patch

from regions import get_enabled_regions


@patch("regions.boto3.client")
def test_get_enabled_regions_filters_opted_in(mock_boto_client):
    mock_ec2 = MagicMock()
    mock_boto_client.return_value = mock_ec2
    mock_ec2.describe_regions.return_value = {
        "Regions": [
            {"RegionName": "us-east-1", "OptInStatus": "opt-in-not-required"},
            {"RegionName": "eu-west-1", "OptInStatus": "opted-in"},
            {"RegionName": "ap-east-1", "OptInStatus": "not-opted-in"},
        ]
    }

    regions = get_enabled_regions()

    assert regions == ["eu-west-1", "us-east-1"]
    mock_boto_client.assert_called_once_with("ec2", region_name="us-east-1")
    mock_ec2.describe_regions.assert_called_once_with(AllRegions=True)
