import pytest
from datetime import datetime, timezone
from ..src.utils import convert_logon_time, parse_date


def test_convert_logon_time():
    logon_time_str = "2023-06-24 12:54:55"
    expected_datetime = datetime(2023, 6, 24, 12, 54, 55)
    assert convert_logon_time(logon_time_str) == expected_datetime


def test_parse_date():
    date_str = "2023-06-24T12:54:55.123456Z"
    actual_datetime = parse_date(date_str).timestamp()
    expected_datetime = datetime(2023, 6, 24, 12, 54, 55, 123456, tzinfo=timezone.utc).timestamp()
    assert actual_datetime == pytest.approx(expected_datetime, abs=1e-3)  # adjust precision here





def test_parse_date_with_extra_precision():
    date_str = "2023-06-24T12:54:55.123456789Z"
    expected_datetime = datetime(2023, 6, 24, 12, 54, 55, 123456, tzinfo=timezone.utc)
    assert parse_date(date_str) == expected_datetime
