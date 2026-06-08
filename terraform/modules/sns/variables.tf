variable "project_name" {
  description = "Project name used in resource naming."
  type        = string
}

variable "notification_email" {
  description = "Email address for cost optimization alerts."
  type        = string
}

variable "tags" {
  description = "Tags applied to SNS resources."
  type        = map(string)
  default     = {}
}
