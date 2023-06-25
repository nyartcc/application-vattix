from _decimal import getcontext, Decimal, ROUND_DOWN
from datetime import datetime, timezone


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


def format_float(value):
    getcontext().prec = 4
    return Decimal(value).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
