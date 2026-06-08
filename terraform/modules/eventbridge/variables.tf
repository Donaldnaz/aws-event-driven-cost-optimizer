variable "project_name" {
  description = "Project name used in resource naming."
  type        = string
}

variable "lambda_function_arn" {
  description = "ARN of the Lambda function to invoke."
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the Lambda function to invoke."
  type        = string
}

variable "schedule_expression" {
  description = "EventBridge schedule expression for nightly runs."
  type        = string
  default     = "cron(0 2 * * ? *)"
}

variable "tags" {
  description = "Tags applied to EventBridge resources."
  type        = map(string)
  default     = {}
}
