variable "aws_region" {
  description = "AWS region for deployment."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used in resource naming."
  type        = string
  default     = "cost-optimizer"
}

variable "notification_email" {
  description = "Email address for cost optimization alerts."
  type        = string
}

variable "snapshot_age_days" {
  description = "Age threshold in days for old snapshot detection."
  type        = number
  default     = 90
}

variable "stopped_instance_days" {
  description = "Days threshold for long-stopped EC2 detection."
  type        = number
  default     = 7
}

variable "report_retention_days" {
  description = "Number of days to retain cost reports in S3."
  type        = number
  default     = 90
}

variable "schedule_expression" {
  description = "EventBridge schedule expression for nightly runs."
  type        = string
  default     = "cron(0 2 * * ? *)"
}

variable "tags" {
  description = "Common tags applied to all resources."
  type        = map(string)
  default = {
    Project   = "cost-optimizer"
    ManagedBy = "terraform"
  }
}
