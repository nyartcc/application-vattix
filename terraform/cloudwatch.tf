resource "aws_cloudwatch_event_rule" "every_minute" {
  name                = "every_minute"
  description         = "Fires every minute"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "every_minute_lambda" {
  rule      = aws_cloudwatch_event_rule.every_minute.name
  arn       = aws_lambda_function.data_collection.arn
  target_id = "every_minute_lambda"

}

