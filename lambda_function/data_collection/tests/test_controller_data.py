import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch

from ..src.controller_data import ControllerDataPreparer

# Instantiate the class to be tested
cdp = ControllerDataPreparer()


# Define a pytest fixture for the mock datetime
@pytest.fixture(autouse=True)
def mock_datetime_now(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return datetime(2023, 4, 10, 11, 31, 28)


def test_calculate_duration(sample_feed):
    logon_time = datetime(2023, 4, 10, 11, 1, 28, tzinfo=timezone.utc)  # 30 minutes before the mocked now
    duration = cdp.calculate_duration(logon_time)

    assert isinstance(duration, Decimal), "Duration should be a Decimal"
    assert duration >= 30, "Duration should be greater than or equal to 30"


def test_prepare_new_controller(sample_feed):
    for controller in sample_feed['controllers']:
        new_controller = cdp.prepare_new_controller(controller.copy())
        assert isinstance(new_controller, dict), "new_controller should be a dictionary"
        assert 'controller_id' in new_controller, "new_controller should have 'controller_id'"
        assert 'session_id' in new_controller, "new_controller should have 'session_id'"
        assert 'duration' in new_controller, "new_controller should have 'duration'"
        assert 'last_updated' in new_controller, "new_controller should have 'last_updated'"


def test_format_existing_controller(sample_feed):
    for controller in sample_feed['controllers']:
        controller['duration'] = Decimal(30.0)  # add duration to controller before method call
        existing_controller = cdp.format_existing_controller(controller.copy())

        assert isinstance(existing_controller, dict), "existing_controller should be a dictionary"
        assert 'last_updated' in existing_controller, "existing_controller should have 'last_updated'"
        assert 'duration' in existing_controller, "existing_controller should have 'duration'"
        assert 'original_duration' in existing_controller, "existing_controller should have 'original_duration'"
