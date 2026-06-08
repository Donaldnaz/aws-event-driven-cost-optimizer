from datetime import datetime, timedelta, timezone

import boto3

from regions import get_enabled_regions

# Rough monthly USD estimates (not billing truth).
EBS_GB_MONTHLY_USD = 0.10
EIP_MONTHLY_USD = 3.60
EC2_STOPPED_MONTHLY_USD = 5.00
SNAPSHOT_GB_MONTHLY_USD = 0.05


def _estimate_ebs_monthly(size_gb: int) -> float:
    return round(size_gb * EBS_GB_MONTHLY_USD, 2)


def _estimate_snapshot_monthly(size_gb: int) -> float:
    return round(size_gb * SNAPSHOT_GB_MONTHLY_USD, 2)


def _scan_unattached_ebs(ec2_client, region: str) -> list:
    findings = []
    paginator = ec2_client.get_paginator("describe_volumes")
    for page in paginator.paginate(Filters=[{"Name": "status", "Values": ["available"]}]):
        for volume in page.get("Volumes", []):
            size_gb = volume.get("Size", 0)
            findings.append(
                {
                    "category": "unattached_ebs",
                    "severity": "medium",
                    "resource_id": volume["VolumeId"],
                    "region": region,
                    "description": f"EBS volume {volume['VolumeId']} ({size_gb} GB) is unattached",
                    "estimated_monthly_savings": _estimate_ebs_monthly(size_gb),
                }
            )
    return findings


def _scan_unused_eips(ec2_client, region: str) -> list:
    findings = []
    response = ec2_client.describe_addresses()
    for address in response.get("Addresses", []):
        if not address.get("AssociationId"):
            findings.append(
                {
                    "category": "unused_eip",
                    "severity": "low",
                    "resource_id": address.get("AllocationId") or address.get("PublicIp"),
                    "region": region,
                    "description": f"Elastic IP {address.get('PublicIp')} is not associated",
                    "estimated_monthly_savings": EIP_MONTHLY_USD,
                }
            )
    return findings


def _scan_stopped_ec2(ec2_client, region: str, stopped_days: int) -> list:
    findings = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=stopped_days)
    paginator = ec2_client.get_paginator("describe_instances")
    for page in paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
    ):
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                launch_time = instance.get("LaunchTime")
                if launch_time and launch_time < cutoff:
                    instance_id = instance["InstanceId"]
                    instance_type = instance.get("InstanceType", "unknown")
                    findings.append(
                        {
                            "category": "long_stopped_ec2",
                            "severity": "medium",
                            "resource_id": instance_id,
                            "region": region,
                            "description": (
                                f"EC2 instance {instance_id} ({instance_type}) "
                                f"has been stopped since before {cutoff.date().isoformat()}"
                            ),
                            "estimated_monthly_savings": EC2_STOPPED_MONTHLY_USD,
                        }
                    )
    return findings


def _scan_old_snapshots(ec2_client, region: str, snapshot_age_days: int) -> list:
    findings = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=snapshot_age_days)
    paginator = ec2_client.get_paginator("describe_snapshots")
    for page in paginator.paginate(OwnerIds=["self"]):
        for snapshot in page.get("Snapshots", []):
            start_time = snapshot.get("StartTime")
            if start_time and start_time < cutoff:
                size_gb = snapshot.get("VolumeSize", 0)
                snap_id = snapshot["SnapshotId"]
                findings.append(
                    {
                        "category": "old_snapshot",
                        "severity": "low",
                        "resource_id": snap_id,
                        "region": region,
                        "description": (
                            f"EBS snapshot {snap_id} ({size_gb} GB) is older than "
                            f"{snapshot_age_days} days"
                        ),
                        "estimated_monthly_savings": _estimate_snapshot_monthly(size_gb),
                    }
                )
    return findings


def _scan_stopped_rds(rds_client, region: str) -> list:
    findings = []
    paginator = rds_client.get_paginator("describe_db_instances")
    for page in paginator.paginate():
        for db in page.get("DBInstances", []):
            if db.get("DBInstanceStatus") == "stopped":
                db_id = db["DBInstanceIdentifier"]
                instance_class = db.get("DBInstanceClass", "unknown")
                findings.append(
                    {
                        "category": "stopped_rds",
                        "severity": "medium",
                        "resource_id": db_id,
                        "region": region,
                        "description": (
                            f"RDS instance {db_id} ({instance_class}) is stopped"
                        ),
                        "estimated_monthly_savings": EC2_STOPPED_MONTHLY_USD,
                    }
                )
    return findings


def get_recommendations(
    region: str,
    snapshot_age_days: int,
    stopped_instance_days: int,
) -> list:
    ec2_client = boto3.client("ec2", region_name=region)
    rds_client = boto3.client("rds", region_name=region)

    findings = []
    findings.extend(_scan_unattached_ebs(ec2_client, region))
    findings.extend(_scan_unused_eips(ec2_client, region))
    findings.extend(_scan_stopped_ec2(ec2_client, region, stopped_instance_days))
    findings.extend(_scan_old_snapshots(ec2_client, region, snapshot_age_days))
    findings.extend(_scan_stopped_rds(rds_client, region))

    findings.sort(
        key=lambda f: f.get("estimated_monthly_savings", 0),
        reverse=True,
    )
    return findings


def get_all_region_recommendations(
    snapshot_age_days: int,
    stopped_instance_days: int,
) -> tuple[list, dict]:
    all_findings = []
    region_errors = {}

    for region in get_enabled_regions():
        try:
            findings = get_recommendations(
                region=region,
                snapshot_age_days=snapshot_age_days,
                stopped_instance_days=stopped_instance_days,
            )
            all_findings.extend(findings)
        except Exception as exc:
            region_errors[region] = str(exc)

    all_findings.sort(
        key=lambda f: f.get("estimated_monthly_savings", 0),
        reverse=True,
    )
    return all_findings, region_errors
