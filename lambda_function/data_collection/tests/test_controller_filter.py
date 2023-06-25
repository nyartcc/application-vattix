from datetime import datetime
import pytest
from ..src.controller_filter import ControllerFilter
from shared.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)


# Define a pytest fixture for the mock datetime
@pytest.fixture(autouse=True)
def mock_datetime_now(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return datetime(2023, 4, 10, 11, 31, 28)


# Define a pytest fixture to create a ControllerFilter instance
@pytest.fixture
def cf(sample_feed):
    return ControllerFilter(sample_feed)


def test_filter_ratings(cf, sample_feed):
    filtered_ratings = cf.filter_ratings()
    for rating in filtered_ratings:
        assert rating['id'] > 1, "Rating ID should be greater than 1"


def test_get_rating_name(cf, sample_feed):
    for rating in sample_feed['ratings']:
        rating_name_long = cf.get_rating_name(rating['id'], 'long')
        rating_name_short = cf.get_rating_name(rating['id'], 'short')

        assert rating_name_long == rating['long'], "Long rating name should match the data feed"
        assert rating_name_short == rating['short'], "Short rating name should match the data feed"


def test_get_facilities_name(cf, sample_feed):
    for facility in sample_feed['facilities']:
        facility_name_long = cf.get_facilities_name(facility['id'], 'long')
        facility_name_short = cf.get_facilities_name(facility['id'], 'short')

        assert facility_name_long == facility['long'], "Long facility name should match the data feed"
        assert facility_name_short == facility['short'], "Short facility name should match the data feed"


def test_filter_facilities(cf, sample_feed):
    filtered_facilities = cf.filter_facilities()
    for facility in filtered_facilities:
        assert facility['id'] >= 1, "Facility ID should be greater than 1"


def test_filter_data_observers_removed(cf, sample_feed):
    # Get controllers with a facility ID greater than 0
    original_controllers = [controller for controller in sample_feed['controllers'] if controller['facility'] > 0]
    logger.debug(f"Original controllers: {original_controllers}")

    filtered_data = cf.filter_data()

    # Get controllers with a facility ID greater than 0 in the filtered data
    filtered_controllers = [controller for controller in filtered_data if controller['facility'] > 0]
    logger.debug(f"Filtered controllers: {filtered_controllers}")

    assert len(filtered_controllers) == len(original_controllers), "All observers should have been filtered out"


def test_filter_data(cf, sample_feed):
    filtered_data = cf.filter_data()
    for controller in filtered_data:
        assert controller['rating'] > 1, "Controller rating should be greater than 1"
        assert controller['facility'] > 1, "Controller facility should be greater than 1"
        assert controller['frequency'] != '199.998', "Controller frequency should not be 199.998"
