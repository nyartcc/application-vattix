from _decimal import ROUND_DOWN
from decimal import Decimal
from datetime import datetime, timezone

from .utils import parse_date
from shared.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)


class ControllerDataPreparer:
    def __init__(self):
        pass

    def calculate_duration(self, logon_time):
        """
        Calculate the duration of the session
        :param logon_time: The logon_time datetime object from the controller data
        :return: str: The duration of the session in minutes
        """

        duration_seconds = (datetime.now(timezone.utc) - logon_time).total_seconds() / 60
        duration_decimal = Decimal(duration_seconds).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        return duration_decimal

    def prepare_new_controller(self, controller):
        """
        Prepare the controller data for writing to the database
        :param controller: The controller data to be prepared
        :return: perpared controller data
        """

        # Map 'cid' to 'controller_id' for DynamoDB
        controller_id: str = str(controller.pop('cid'))

        # Truncate the extra precision from the 'logon_time' string
        logon_time_str: str = parse_date(controller['logon_time'])
        logger.debug(f"logon_time_str: {logon_time_str}")

        # Convert the 'logon_time' to a format suitable for session_id
        logon_time = parse_date(controller['logon_time'])
        logger.debug(f"logon_time: {logon_time}")

        session_id = f"{controller_id}-{logon_time.strftime('%Y%m%d%H%M%S%f')}"
        logger.debug(f"session_id: {session_id}")

        # Calculate the duration for a new controller
        duration = self.calculate_duration(logon_time)

        # Add the session_id and initial duration and last_updated to the controller
        controller['controller_id'] = controller_id
        controller['session_id'] = session_id
        controller['duration'] = duration
        controller['last_updated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        logger.debug(f"Controller: {controller}")

        return controller

    def format_existing_controller(self, existing_controller):
        """
        Calculate the duration and format controller data.
        :param existing_controller: The existing controller data
        :return: The updated controller data
        """

        # Get data from the existing controller
        original_duration = existing_controller['duration']

        # Use the original logon_time when calculating the duration
        original_logon_time_str = existing_controller['logon_time']
        logger.debug(f"original_logon_time_str: {original_logon_time_str}")

        original_logon_time: datetime = parse_date(original_logon_time_str)

        # Calculate the duration
        duration = self.calculate_duration(original_logon_time)

        # Update the controller
        existing_controller['last_updated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        existing_controller['duration'] = duration
        existing_controller['original_duration'] = original_duration

        logger.info(f"Duration: {duration}")

        return existing_controller
