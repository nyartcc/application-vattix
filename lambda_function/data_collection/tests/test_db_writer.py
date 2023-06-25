import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from ..src.db_writer import DBWriter


@pytest.fixture
def sample_data():
    return {
        "controllers": [
            {
                "callsign": "TEST_CALLSIGN",
                "controller_id": "TEST_ID",
                "logon_time": "20230619100000",
                "session_id": "TEST_SESSION_ID",
                "duration": Decimal(60.00)
            }
        ]
    }


@patch("data_collection.src.db_writer.DBClient")
@patch("data_collection.src.db_writer.ControllerFilter")
@patch("data_collection.src.db_writer.ControllerDataPreparer")
def test_write(MockControllerDataPreparer, MockControllerFilter, MockDBClient, sample_data):
    # Add an existing controller to the return value of get_all_items
    MockDBClient.return_value.get_all_items.return_value = [sample_data["controllers"][0]]

    MockControllerFilter.return_value.filter_data.return_value = sample_data["controllers"]
    MockControllerDataPreparer.return_value.prepare_new_controller.return_value = sample_data["controllers"][0]
    MockControllerDataPreparer.return_value.format_existing_controller.return_value = sample_data["controllers"][0]

    db_writer = DBWriter(sample_data)
    result = db_writer.write()

    # Assert the DBClient, ControllerFilter and ControllerDataPreparer methods were called correctly
    MockDBClient.return_value.get_all_items.assert_called_once()
    MockControllerFilter.return_value.filter_data.assert_called_once()
    MockControllerDataPreparer.return_value.prepare_new_controller.assert_called_with(sample_data["controllers"][0])
    MockControllerDataPreparer.return_value.format_existing_controller.assert_called_with(sample_data["controllers"][0])

    # Assert the DBClient update_item method was called with the correct arguments
    MockDBClient.return_value.update_item.assert_called_with(sample_data["controllers"][0], sample_data["controllers"][0]['duration'])

    # Assert the result is as expected
    assert result == {'num_controllers': 1, 'num_new_controllers': 0, 'num_existing_controllers': 1}
