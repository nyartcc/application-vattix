import json
import sys

sys.path.append('/opt')

import src.data_fetcher as data_fetcher
from src.db_writer import DBWriter
from shared.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)

# Create a dictionary to hold our execution counts
execution_counts = {}


def lambda_handler(event, context):
    """
    AWS Lambda function handler for the Vattix data collector.

    This function is triggered based on the AWS Lambda service configuration.
    The event and context parameters are standard parameters for a Lambda handler
    and provide details about the invocation, function, and execution environment.

    The function performs the following steps:
        1. Logs the start of the Lambda invocation.
        2. Fetches data from an external API using the data_fetcher module.
        3. Logs the fetched data (in debug mode to prevent outputting sensitive information in regular logs).
        4. Initializes an instance of the DBWriter class.
        5. Writes the fetched data to a DynamoDB database using the DBWriter instance.
        6. Logs the successful completion of the Lambda invocation.

    If any step of the function execution raises an exception, the function logs
    the error message and returns an HTTP 500 status code along with the error message.
    If the function executes successfully, it returns an HTTP 200 status code and a
    success message.

    :param event: An event data dict provided by AWS Lambda service. Not used in this function.
    :param context: A context object provided by AWS Lambda service with runtime information. Not used in this function.
    :return: A dict with 'statusCode' and 'body' keys. The 'statusCode' is an HTTP
             status code indicating the function execution result (200 for success, 500 for errors).
             The 'body' is a string providing details about the function execution result.
    """

    # Check if AWS credentials or permissions are missing
    if not data_fetcher.check_aws_credentials():
        return {
            'statusCode': 500,
            'body': json.dumps('AWS credentials or permissions are missing. '
                               'Please check that your AWS credentials are configured correctly '
                               'and that the IAM role assigned to this Lambda function has '
                               'the correct permissions.')
        }

    try:
        logger.info(f"Lambda invocation started")
        logger.info(f"Fetching data from API")
        data = data_fetcher.fetch()

        logger.debug(f"Data fetched: {data}")  # Use debug level to prevent sensitive data output in normal logs
        writer = DBWriter(data)

        logger.info(f"Writing data to DynamoDB")
        write = writer.write()

        logger.info(f"Lambda invocation completed successfully")

        write_new_controllers = write['num_new_controllers']
        write_existing_controllers = write['num_existing_controllers']
        write_num_controllers = write['num_controllers']

        logger.info(f'Wrote {write_num_controllers} controllers to DynamoDB. ')
        logger.info(f'{write_new_controllers} new controllers and {write_existing_controllers} existing controllers.')

        return {
            'statusCode': 200,
            'body': json.dumps(f'Data fetch and write to DynamoDB completed successfully! Wrote '
                               f'{write_num_controllers} controllers to DynamoDB. '
                               f'{write_new_controllers} new controllers and '
                               f'{write_existing_controllers} existing controllers.')
        }

    except Exception as e:
        logger.error(f"An error occurred during lambda_function invocation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred during lambda_function invocation: {str(e)}')
        }


if __name__ == "__main__":
    # Only for local testing:
    # Read event and context from the command-line argument
    logger.warning(f"Running lambda_handler locally")
    event_str, context_str = sys.argv[1].split()
    event = json.loads(event_str)
    context = json.loads(context_str)
    lambda_handler(event, context)
