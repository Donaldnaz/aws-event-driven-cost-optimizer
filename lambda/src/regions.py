import boto3

ENABLED_OPT_IN_STATUSES = (None, "opt-in-not-required", "opted-in")


def get_enabled_regions() -> list[str]:
    client = boto3.client("ec2", region_name="us-east-1")
    response = client.describe_regions(AllRegions=True)
    regions = []
    for region in response.get("Regions", []):
        if region.get("OptInStatus") in ENABLED_OPT_IN_STATUSES:
            regions.append(region["RegionName"])
    return sorted(regions)
