output "bucket_name" {
  description = "Name of the S3 bucket for cost reports."
  value       = aws_s3_bucket.reports.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 bucket for cost reports."
  value       = aws_s3_bucket.reports.arn
}
