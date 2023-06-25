from shared.api_client import APIClient
import os

from shared.logger import setup_logger
from shared.metrics import publish_metrics

# Set up logging
logger = setup_logger(__name__)

# Create a dictionary to hold our execution counts
execution_counts = {}


def fetch():
    """
    Fetch the data from the API
    :return: The data obviously
    """

    try:
        logger.info(f"Reading API_URL from environment variable")
        API_URL = os.environ.get('API_URL')
        if API_URL is None:
            raise KeyError
        logger.info(f"API_URL: {API_URL}")
    except KeyError:
        logger.critical(f"API_URL environment variable not set")
        API_URL = 'https://data.vatsim.net/v3/vatsim-data.json'
        raise Exception('API_URL environment variable not set')

    publish_metrics('DataFetch')

    logger.info(f"Fetching data from API: {API_URL}")
    try:
        api_client = APIClient(API_URL)
        logger.info(f"Data fetched from API")
    except Exception as e:
        logger.critical(f"Unable to fetch data from API: {e}")
        publish_metrics('DataFetchError')
        raise Exception(f"Unable to fetch data from API: {e}")

    execution_counts['fetch'] = execution_counts.get('fetch', 0) + 1

    return api_client.get_data()


def check_aws_credentials():
    """
    Check that the AWS credentials are available
    :return:  True if available, False otherwise
    """

    # Check AWS credentials when running locally
    logger.info(f"Checking AWS credentials")
    try:
        logger.info(f"Reading AWS credentials from environment variables")
        AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
        AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')

        if AWS_ACCESS_KEY_ID is None or AWS_SECRET_ACCESS_KEY is None or AWS_DEFAULT_REGION is None:
            raise KeyError
        logger.info(f"SUCCESS: AWS credentials set")
        logger.info(f"AWS_ACCESS_KEY_ID: {AWS_ACCESS_KEY_ID}")
        # logger.info(f"AWS_SECRET_ACCESS_KEY: {AWS_SECRET_ACCESS_KEY}")
        logger.info(f"AWS_DEFAULT_REGION: {AWS_DEFAULT_REGION}")

    except KeyError:
        logger.critical(f"AWS credentials not set")
        raise Exception('AWS credentials not set')

    # If running on AWS, credentials will be provided by IAM role so no need to check
    return True
