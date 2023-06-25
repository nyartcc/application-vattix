from datetime import datetime, timezone


def convert_logon_time(logon_time_str):
    logon_time = datetime.strptime(logon_time_str, '%Y-%m-%d %H:%M:%S')
    return logon_time


def parse_date(date_str):
    """
    Parse a date string in the format '%Y-%m-%dT%H:%M:%S.%fZ' and return a datetime object.
    If the date string has more than 6 digits for the fractional second then truncate it to 6 digits.
    :param date_str: The date string to parse
    :return: The datetime object in the format '%Y-%m-%dT%H:%M:%S.%fZ'
    """
    # Truncate the extra precision from the 'logon_time' string
    date_parts = date_str.split('.')
    if len(date_parts[1]) > 6:
        date_parts[1] = date_parts[1][:6] + "Z"  # keep 6 digits of precision
        date_str = '.'.join(date_parts)

    datetime_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)  # Add timezone information

    return datetime_obj

