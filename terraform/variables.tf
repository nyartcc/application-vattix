variable "aws_region" {
  default = "us-east-1"
  type    = string
}

variable "collector_lambda_function_name" {
  default     = "vattix_data_collector"
  type        = string
  description = "The name of the lambda function that will collect the data from the VATSIM JSON feed"
}

variable "collector_lambda_function_description" {
  default     = "Author: KM. Collects data from the VATSIM JSON feed and stores it in DynamoDB"
  type        = string
  description = "Author: KM. Description: Collects data from the VATSIM JSON feed and stores it in DynamoDB"
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table that stores sessions from the VATSIM JSON feed"
  type        = string
  default     = "vattix_controller_sessions"
}

variable "dev_dynamodb_table_name" {
  description = "For DEVELOPMENT The name of the DynamoDB table that stores sessions from the VATSIM JSON feed"
  type        = string
  default     = "dev_vattix_controller_sessions"
}

variable "api_url" {
  description = "The URL of the VATSIM JSON feed"
  type        = string
  default     = "https://data.vatsim.net/v3/vatsim-data.json"
}