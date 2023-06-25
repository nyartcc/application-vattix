# controller_filter.py
from shared.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)


class ControllerFilter:
    def __init__(self, data):
        self.data = data

    def filter_ratings(self, min_rating_short='OBS', min_rating_long='Observer'):
        """
        Filter the data to remove controllers with rating lower than specified
        :param min_rating_short:  The minimum rating short name (Defaults to OBS)
        :param min_rating_long:   The minimum rating long name (Defaults to Observer)
        :return:                The filtered data
        """

        logger.debug(f"Filtering data to remove ratings lower than {min_rating_short} ({min_rating_long})")

        ratings = self.data['ratings']
        min_rating_id = next((rating['id'] for rating in ratings if
                              rating['short'] == min_rating_short or rating['long'] == min_rating_long), None)
        if min_rating_id is not None:
            return [rating for rating in ratings if rating['id'] > min_rating_id]
        else:
            raise ValueError(f"Minimum rating '{min_rating_short}' or '{min_rating_long}' not found in the data feed.")

    def get_rating_name(self, rating_id, name_type='long'):
        """
        Get the name of a rating from the data feed
        :param self:      The ControllerFilter instance
        :param rating_id:  The rating ID
        :param name_type:  The name type (short or long)
        :return:        The name of the rating
        """

        ratings = self.data['ratings']
        name = next((rating[name_type] for rating in ratings if rating['id'] == rating_id), None)
        if name is not None:
            return name
        else:
            raise ValueError(f"Rating ID '{rating_id}' not found in the data feed.")

    def get_facilities_name(self, facility_id, name_type='long'):
        """
        Get the name of a facility from the data feed
        :param self:      The ControllerFilter instance
        :param facility_id:  The facility ID
        :param name_type:  The name type (short or long)
        :return:      The name of the facility
        """

        facilities = self.data['facilities']
        name = next((facility[name_type] for facility in facilities if facility['id'] == facility_id), None)
        if name is not None:
            return name
        else:
            raise ValueError(f"Facility ID '{facility_id}' not found in the data feed.")

    def filter_facilities(self, min_facility_short='OBS', min_facility_long='Observer'):
        """
        Filter the data to remove controllers with rating lower than specified
        :param self:            The ControllerFilter instance
        :param min_facility_short:  The minimum facility short name (Defaults to OBS)
        :param min_facility_long:  The minimum facility long name (Defaults to Observer)
        :return:              The filtered data
        """

        facilities = self.data['facilities']
        min_facility_id = next((facility['id'] for facility in facilities if
                                facility['short'] == min_facility_short or facility['long'] == min_facility_long), None)
        if min_facility_id is not None:
            return [facility for facility in facilities if facility['id'] > min_facility_id]
        else:
            raise ValueError(
                f"Minimum facility '{min_facility_short}' or '{min_facility_long}' not found in the data feed.")

    def filter_data(self):
        """
        Filter the data to remove controllers with rating lower than OBS or facilities lower than FSS
        :return: The filtered data
        """
        logger.debug(f"Filtering data: {self.data}")

        # Get all ratings higher than OBS
        higher_than_observer_ratings = self.filter_ratings()
        logger.debug(f"Rating IDs: {higher_than_observer_ratings}")

        # Get all facilities higher than OBS
        higher_than_observer_facilities = self.filter_facilities()
        logger.debug(f"Facility IDs: {higher_than_observer_facilities}")

        # Filtered out controllers with rating higher than OBS or facilities higher than FSS
        filtered_data = [controller for controller in self.data['controllers'] if
                         any(d['id'] == controller['rating'] for d in higher_than_observer_ratings) and
                         any(d['id'] == controller['facility'] for d in higher_than_observer_facilities) and
                         controller['frequency'] != '199.998']

        return filtered_data