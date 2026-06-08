import os


def get_config():
    return {
        "report_bucket": os.environ["REPORT_BUCKET"],
        "sns_topic_arn": os.environ["SNS_TOPIC_ARN"],
        "snapshot_age_days": int(os.environ.get("SNAPSHOT_AGE_DAYS", "90")),
        "stopped_instance_days": int(os.environ.get("STOPPED_INSTANCE_DAYS", "7")),
        "aws_region": os.environ.get("AWS_REGION", "us-east-1"),
    }
