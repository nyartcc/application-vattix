import os
import logging
from decimal import Decimal

from shared.db_client import DBClient
from shared.metrics import publish_metrics
from shared.logger import setup_logger
from .controller_filter import ControllerFilter
from .controller_data import ControllerDataPreparer

# Set up logging
logger = setup_logger(__name__)

# Create a dictionary to hold our execution counts
execution_counts = {}

try:
    logger.info(f"Reading DYNAMODB_TABLE_NAME from environment variable")
    DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
    logger.info(f"DYNAMODB_TABLE_NAME: {DYNAMODB_TABLE_NAME}")
except KeyError:
    DYNAMODB_TABLE_NAME = 'vatsimControllerStatistics'
    logger.critical(f"DYNAMODB_TABLE_NAME environment variable not set")
    raise Exception('DYNAMODB_TABLE_NAME environment variable not set')


class DBWriter:
    def __init__(self, data):
        self.db_client = DBClient(DYNAMODB_TABLE_NAME)
        self.controller_filter = ControllerFilter(data)
        self.controller_data_preparer = ControllerDataPreparer()  # Create an instance of ControllerDataPreparer
        self.data = data

    def write(self):
        """
        Write the data to DynamoDB
        :param data: The data to write
        :return: True if successful, False otherwise
        """
        publish_metrics('DatabaseWrite')

        # DEBUG
        logger.debug(f"Writing data to DynamoDB: {self.data}")

        # Counter for the number of controllers
        num_controllers = 0
        num_new_controllers = 0
        num_existing_controllers = 0

        # Fetch all existing controllers from the DB
        existing_controllers = self.db_client.get_all_items()
        logger.debug(f"Existing controllers: {existing_controllers}")

        existing_session_ids = [controller.get('session_id') for controller in existing_controllers]
        existing_controllers_dict = {controller['session_id']: controller for controller in existing_controllers}

        # Filter the data to remove controllers with rating lower than OBS or facilities lower than FSS
        filtered_data = self.controller_filter.filter_data()  # Use the filter_data method from the ControllerFilter instance

        for controller in filtered_data:
            # DEBUG
            logger.debug(f"Controller: {controller}")

            # Prepare the controller data for writing to the database
            prepared_controller = self.controller_data_preparer.prepare_new_controller(controller)  # Use the
            # prepare_new_controller_data method from the ControllerDataPreparer instance

            # Check if the controller is already in the database
            if prepared_controller['session_id'] in existing_session_ids:

                existing_controller = existing_controllers_dict[prepared_controller['session_id']]

                existing_controller = self.controller_data_preparer.format_existing_controller(existing_controller)  # Use the
                # prepare_existing_controller_data method from the ControllerDataPreparer instance

                # Update the controller in DynamoDB
                self.db_client.update_item(existing_controller, existing_controller['duration'])
                logger.info(
                    f"Updated existing controller with session_id: {prepared_controller['session_id']} in DynamoDB")

                # Increment the number of controllers
                num_controllers += 1
                num_existing_controllers += 1

            else:
                # Write the prepared_controller to DynamoDB
                try:
                    self.db_client.put_item(prepared_controller)
                    logger.info(
                        f"New controller added: {prepared_controller['callsign']} ({prepared_controller['controller_id']}) - "
                        f"{prepared_controller['logon_time']} (UTC) - {prepared_controller['duration']} minutes. "
                        f"Session ID:"
                        f" {prepared_controller['session_id']}")

                    # Increment the number of controllers
                    num_controllers += 1
                    num_new_controllers += 1

                except Exception as e:
                    logger.error(f"Error writing controller to DynamoDB: {e}")
                    return False

            logger.info(f"Number of controllers: {num_controllers}")

        # Publish metrics to CloudWatch
        publish_metrics('NumNewControllers', value=num_new_controllers)
        logger.debug(f"[METRIC]: NumNewControllers: {num_new_controllers}")

        publish_metrics('NumExistingControllers', value=num_existing_controllers)
        logger.debug(f"[METRIC]: NumNewControllers: {num_existing_controllers}")

        return {'num_controllers': num_controllers, 'num_new_controllers': num_new_controllers,
                'num_existing_controllers': num_existing_controllers}
