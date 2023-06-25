import os
import sys
import json
from shared import logger
from processor import DataProcessor

# Set up logging
logger = logger.setup_logger(__name__)

# Get environment variables
dynamodb_table = os.environ['DYNAMODB_TABLE_NAME']


def lambda_handler(event, context):
    """
    AWS Lambda function for VATTIX data processing.

    This function is triggered by a CloudWatch Event Rule on a schedule, once per week.
    It fetches the data from the DynamoDB table, processes it, and generates a report.

    The function does the following steps:
        1. Set up a DataProcessor instance.
        2. Get the current week date range.
        3. Fetch all sessions in the given week.
        4. Group by "callsign" and calculate total duration.
        5. Calculate percentage and sort.
        6. Generate report.
        7. Return report.

    :param event: An event data dict provided by AWS Lambda service. Not used in this function.
    :param context: A context object provided by AWS Lambda service with runtime information. Not used in this function.
    :return: A dict with 'statusCode' and 'body' keys. The 'statusCode' is an HTTP status code indicating the function
                execution result (200 for success, 500 for errors). The 'body' is a string providing details about the
                function execution result.
    """

    # Log start of Lambda invocation
    logger.info(f"Lambda invocation started")

    # Check if running locally or in AWS
    if 'AWS_EXECUTION_ENV' in os.environ:
        logger.info(f"Running in AWS Lambda...")
    else:
        logger.warning(f"Running locally...")

        # Set up processor
    processor = DataProcessor(dynamodb_table)

    # Get the current week date range
    week_start, week_end = processor.get_week_range()

    # Fetch all sessions in the given week
    items = processor.fetch_sessions(week_start, week_end)

    # Group by "callsign" and calculate total duration
    callsigns, total_duration, total_overlap, uptime_hours = processor.calculate_durations(items)

    # Calculate percentage, hours and sort
    sorted_callsigns = processor.calculate_percentages(callsigns)


    # Generate report
    logger.info(f"Generating report...")
    report = {'week_start': week_start.strftime('%Y-%m-%d'), 'week_end': week_end.strftime('%Y-%m-%d'),
                                                             'callsigns': sorted_callsigns}
    logger.debug(f"Report: {json.dumps(report, indent=4)}")
    print(json.dumps(report, indent=4))

    # Return report
    logger.info(f"Returning report...")
    return {
        'statusCode': 200,
        'body': json.dumps(report)
    }


if __name__ == "__main__":
    # Only for local testing:
    # Read event and context from the command-line argument
    logger.warning(f"Running lambda_handler locally")
    logger.warning(f"AWS Key and Secret are required to run this locally")
    logger.info(f"AWS Region: {os.environ['AWS_REGION']}")
    logger.info(f"AWS Key ID: {os.environ['AWS_ACCESS_KEY_ID']}")
    logger.info(f"AWS DynamoDB Table: {dynamodb_table}")

    event_str, context_str = sys.argv[1].split()
    event = json.loads(event_str)
    context = json.loads(context_str)

    lambda_handler(event, context)
