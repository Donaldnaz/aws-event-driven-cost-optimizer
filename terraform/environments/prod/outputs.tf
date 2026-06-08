output "report_bucket_name" {
  description = "S3 bucket storing JSON cost reports."
  value       = module.s3.bucket_name
}

output "sns_topic_arn" {
  description = "SNS topic ARN for email notifications."
  value       = module.sns.topic_arn
}

output "lambda_function_name" {
  description = "Name of the cost analyzer Lambda function."
  value       = module.lambda.function_name
}

output "lambda_function_arn" {
  description = "ARN of the cost analyzer Lambda function."
  value       = module.lambda.function_arn
}

output "eventbridge_rule_name" {
  description = "EventBridge rule triggering nightly scans."
  value       = module.eventbridge.rule_name
}
