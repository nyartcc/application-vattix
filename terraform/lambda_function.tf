# Create a ZIP file with the 'data_collection_app' code
data "archive_file" "data_collection_app" {
  type        = "zip"
  source_dir  = "../lambda_function/data_collection/"
  output_path = "${path.module}/.terraform/resources/data_collection_app.zip"
}

# Create a ZIP file with the 'data_processing_app' code
data "archive_file" "data_processing_app" {
  type        = "zip"
  source_dir  = "../lambda_function/data_processing/"
  output_path = "${path.module}/.terraform/resources/data_processing_app.zip"
}


data "external" "shared_directory_hash" {
  program = ["sh", "-c", "find ${path.module}/../lambda_function/shared -type f -exec md5 -q {} \\; | sort | md5 | jq -R '{md5: .}'"]
}

# Copy the 'shared' directory to the 'lambda_function/python' directory
# This is a clusterfuck to create a 'python' directory so that Lambda gets the proper formatting
# without having to fuck up the app code.

# Yeah this is... Not great.
resource "null_resource" "prepare_shared_layer" {
  triggers = {
    source_code_hash = data.external.shared_directory_hash.result["md5"]
  }

  provisioner "local-exec" {
    command = <<EOF
    mkdir -p ${path.module}/lambda/python/shared
    cp -R ${path.module}/../lambda/shared/* ${path.module}/lambda/python/shared/
    EOF
  }
}

data "archive_file" "shared_layer" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/python"
  output_path = "${path.module}/.terraform/resources/shared_layer.zip"
}


# Create a ZIP file for the 'requests' layer
data "archive_file" "libraries_layer" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/libraries"
  output_path = "${path.module}/.terraform/resources/requests_layer.zip"
}

# Create the 'requests' Lambda layer
resource "aws_lambda_layer_version" "requests_lambda_layer" {
  layer_name = "requests_lambda_layer"
  compatible_runtimes = [
    "python3.10"
  ]
  filename         = data.archive_file.libraries_layer.output_path
  source_code_hash = filebase64sha256(data.archive_file.libraries_layer.output_path)
}



resource "aws_lambda_layer_version" "shared_lambda_layer" {
  layer_name = "vattix-shared-layer"
  compatible_runtimes = [
    "python3.10"
  ]
  filename         = data.archive_file.shared_layer.output_path
  source_code_hash = data.archive_file.shared_layer.output_base64sha256
}


resource "aws_lambda_function" "data_collection" {
  function_name    = var.collector_lambda_function_name
  filename         = data.archive_file.data_collection_app.output_path
  description      = var.collector_lambda_function_description
  source_code_hash = data.archive_file.data_collection_app.output_base64sha256
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "handler.lambda_handler"
  timeout          = 180

  runtime = "python3.10"

  layers = [
    aws_lambda_layer_version.shared_lambda_layer.arn,
    aws_lambda_layer_version.requests_lambda_layer.arn
  ]

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.vatsim_controller_statistics.name
      API_URL             = var.api_url
    }
  }
}