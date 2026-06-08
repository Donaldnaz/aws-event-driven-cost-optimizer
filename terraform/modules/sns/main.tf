resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-cost-alerts"

  tags = merge(var.tags, {
    Name = "${var.project_name}-cost-alerts"
  })
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.notification_email
}
