variable "project_name" {
  description = "Project name used in resource naming."
  type        = string
}

variable "account_id" {
  description = "AWS account ID for unique bucket naming."
  type        = string
}

variable "report_retention_days" {
  description = "Number of days to retain cost reports before expiration."
  type        = number
  default     = 90
}

variable "tags" {
  description = "Tags applied to S3 resources."
  type        = map(string)
  default     = {}
}
