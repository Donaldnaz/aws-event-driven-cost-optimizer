resource "aws_cloudwatch_event_rule" "nightly" {
  name                = "${var.project_name}-nightly-cost-scan"
  description         = "Triggers the cost optimizer Lambda every night at 02:00 UTC"
  schedule_expression = var.schedule_expression

  tags = merge(var.tags, {
    Name = "${var.project_name}-nightly-cost-scan"
  })
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.nightly.name
  target_id = "cost-analyzer-lambda"
  arn       = var.lambda_function_arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.nightly.arn
}
