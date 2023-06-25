# test_data_fetcher.py
import pytest
import os
from unittest.mock import patch
from ..src.data_fetcher import fetch


@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    monkeypatch.setenv('API_URL', 'https://data.vatsim.net/v3/vatsim-data.json')


@patch('data_collection.src.data_fetcher.APIClient')
def test_fetch_success(mock_api_client):
    # Arrange
    mock_data = {"key": "value"}
    mock_api_client.return_value.get_data.return_value = mock_data

    # Act
    result = fetch()

    # Assert
    mock_api_client.assert_called_once()
    assert result == mock_data


@patch('data_collection.src.data_fetcher.APIClient')
def test_fetch_failure(mock_api_client):
    # Arrange
    mock_api_client.return_value.get_data.side_effect = Exception("Unable to fetch data")

    # Act & Assert
    with pytest.raises(Exception) as e:
        fetch()
    assert "Unable to fetch data" in str(e.value)


@patch('data_collection.src.data_fetcher.APIClient')
def test_fetch_execution_count(mock_api_client):
    # Arrange
    mock_data = {"key": "value"}
    mock_api_client.return_value.get_data.return_value = mock_data

    # Act
    fetch()
    fetch()

    # Assert
    assert mock_api_client.return_value.get_data.call_count == 2
