terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
  account_id    = data.aws_caller_identity.current.account_id
  lambda_source = abspath("${path.module}/../../../lambda/src")
}

module "s3" {
  source = "../../modules/s3"

  project_name          = var.project_name
  account_id            = local.account_id
  report_retention_days = var.report_retention_days
  tags                  = var.tags
}

module "sns" {
  source = "../../modules/sns"

  project_name       = var.project_name
  notification_email = var.notification_email
  tags               = var.tags
}

module "lambda" {
  source = "../../modules/lambda"

  project_name          = var.project_name
  aws_region            = var.aws_region
  source_path           = local.lambda_source
  report_bucket_name    = module.s3.bucket_name
  report_bucket_arn     = module.s3.bucket_arn
  sns_topic_arn         = module.sns.topic_arn
  snapshot_age_days     = var.snapshot_age_days
  stopped_instance_days = var.stopped_instance_days
  tags                  = var.tags
}

module "eventbridge" {
  source = "../../modules/eventbridge"

  project_name         = var.project_name
  lambda_function_arn  = module.lambda.function_arn
  lambda_function_name = module.lambda.function_name
  schedule_expression  = var.schedule_expression
  tags                 = var.tags
}
