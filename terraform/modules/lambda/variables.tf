variable "project_name" {
  description = "Project name used in resource naming."
  type        = string
}

variable "aws_region" {
  description = "AWS region for the Lambda function."
  type        = string
}

variable "source_path" {
  description = "Path to the Lambda source directory."
  type        = string
}

variable "report_bucket_name" {
  description = "S3 bucket name for cost reports."
  type        = string
}

variable "report_bucket_arn" {
  description = "S3 bucket ARN for cost reports."
  type        = string
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for notifications."
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

variable "memory_size" {
  description = "Lambda memory in MB."
  type        = number
  default     = 256
}

variable "timeout" {
  description = "Lambda timeout in seconds."
  type        = number
  default     = 600
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 14
}

variable "tags" {
  description = "Tags applied to Lambda resources."
  type        = map(string)
  default     = {}
}
