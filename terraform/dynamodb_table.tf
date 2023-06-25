resource "aws_dynamodb_table" "vatsim_controller_statistics" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "controller_id"
  range_key    = "logon_time"

  attribute {
    name = "controller_id"
    type = "S"
  }
  attribute {
    name = "logon_time"
    type = "S"
  }
}

resource "aws_dynamodb_table" "dev_vatsim_controller_statistics" {
  name         = var.dev_dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "controller_id"
  range_key    = "logon_time"

  attribute {
    name = "controller_id"
    type = "S"
  }
  attribute {
    name = "logon_time"
    type = "S"
  }
}
