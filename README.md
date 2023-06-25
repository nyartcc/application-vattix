![VATTIX](.github/vattix_github_banner.png)
# VATTIX - A VATSIM Statistic Service

[![codecov](https://codecov.io/gh/Sequal32/VATTIX/branch/master/graph/badge.svg)](https://codecov.io/gh/Sequal32/VATTIX)
[![GitHub license](https://img.shields.io/github/license/Sequal32/VATTIX.svg)](

Current version: `v0.1.0`

## What is VATTIX?
VATTIX is a VATSIM statistic service, which provides a RESTful API to access the data. The data is collected from the VATSIM API and stored in a database. The API provides access to the data in a JSON format.

## How to use VATTIX?
VATTIX is a RESTful API which provides access to the data in a JSON format. 
Currently the API is only available for internal use, but will be made public in the future.

## Current features
The current features of VATTIX are:

- [x] Collect data from the VATSIM API
- [x] Store data in a database
- [x] Provides a Lambda function to access the data
- [x] Provides a Lambda function to generate a weekly report
- [ ] Provides a RESTful API to access the data
- [ ] Provides a RESTful API to access the weekly report
- [ ] Provides a web interface to access the data
- [ ] Provides a web interface to access the weekly report
- [ ] Provides a web interface to access the data and weekly report


## Requirements
VATTIX requires the following software to be installed:

- Python 3.10
- PIP
- AWS Lambda
- AWS DynamoDB
- AWS API Gateway
- Terraform

## Installation
To install VATTIX, follow the steps below:

1. Clone the repository
2. Install the required packages with `pip install -r requirements.txt`
3. Navigate to the `terraform` directory
4. Make sure you have the AWS credentials configured including the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
5. Make sure you have the AWS region configured including the `AWS_DEFAULT_REGION`
6. Change the `terraform.tfvars` file to your needs
7. Run `terraform init`
8. Run `terraform apply`

### Endpoints
The API provides the following endpoints:

#### /v1/statistics/
This endpoint provides access to the statistics of the VATSIM network. The statistics are divided into the following categories:

##### /v1/statistics/controllers/
This endpoint provides access to the statistics of the controllers on the VATSIM network. The statistics are divided into the following categories:

###### /v1/statistics/controllers/top/
This endpoint provides access to the top 25 ATC positions on the VATSIM network. The statistics are divided into the 
following 
categories:

| Category | Description                                           |
|----------|-------------------------------------------------------|
| `callsign` | The callsign of the ATC position.                     |
| `hours` | The amount of hours the ATC position has been online. |
| `percentage` | The percentage of the specified week the ATC position has been online. |
| `start` | The start date of the specified week. |
| `end` | The end date of the specified week. |

###### /v1/statistics/controllers/week/<number>
This endpoint provides access to the statistics of the ATC positions on the VATSIM network for the specified week. 
