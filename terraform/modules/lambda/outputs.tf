output "function_name" {
  description = "Name of the cost analyzer Lambda function."
  value       = aws_lambda_function.analyzer.function_name
}

output "function_arn" {
  description = "ARN of the cost analyzer Lambda function."
  value       = aws_lambda_function.analyzer.arn
}

output "role_arn" {
  description = "ARN of the Lambda execution role."
  value       = aws_iam_role.lambda.arn
}
