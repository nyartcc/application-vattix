resource "aws_api_gateway_rest_api" "vatsim_data_api" {
  name        = "VATSIMDataAPI"
  description = "API for retrieving VATSIM controller data"
}

resource "aws_api_gateway_resource" "controller" {
  rest_api_id = aws_api_gateway_rest_api.vatsim_data_api.id
  parent_id   = aws_api_gateway_rest_api.vatsim_data_api.root_resource_id
  path_part   = "controller"
}

resource "aws_api_gateway_method" "controller_get" {
  rest_api_id   = aws_api_gateway_rest_api.vatsim_data_api.id
  resource_id   = aws_api_gateway_resource.controller.id
  http_method   = "GET"
  authorization = "NONE"
}
