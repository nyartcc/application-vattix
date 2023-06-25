from _decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta, timezone
from shared import logger
from utils import parse_date, format_float


class DataProcessor:
    def __init__(self, table_name):
        self.logger = logger.setup_logger(__name__)
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def parse_date(self, date_str):
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

    def get_week_range(self, week_number=None, start_date=None):
        if week_number is not None:
            # Convert week number to a date, assuming week_number is relative to start of the year
            week_start = datetime.now().replace(month=1, day=1) + timedelta(weeks=week_number - 1)
            week_end = week_start + timedelta(days=7)
        elif start_date is not None:
            # Parse the start_date string into a datetime object
            week_start = datetime.strptime(start_date, '%Y-%m-%d')
            week_end = week_start + timedelta(days=7)
        else:
            # Default to current week
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            week_end = week_start + timedelta(days=7)

        self.logger.info(f"Week start: {week_start.strftime('%Y-%m-%d')}")
        self.logger.info(f"Week end: {week_end.strftime('%Y-%m-%d')}")
        return week_start, week_end

    def fetch_sessions(self, week_start, week_end):
        self.logger.info("Fetching all sessions in the given week...")
        self.logger.debug(f"Scanning DynamoDB table: {self.table}")

        # Format the week_start and week_end to match the format of the 'logon_time' in the DynamoDB table
        week_start_str = week_start.strftime('%Y-%m-%dT%H:%M:%S') + '.000000Z'
        week_end_str = week_end.strftime('%Y-%m-%dT%H:%M:%S') + '.000000Z'

        response = self.table.scan(
            FilterExpression=Key('logon_time').between(week_start_str, week_end_str)
        )
        self.logger.debug("Scan response: {}".format(response))
        self.logger.info("Number of items returned: {}".format(len(response['Items'])))

        return response['Items']

    def calculate_durations(self, items):
        self.logger.info(f"Calculating total duration...")
        callsigns: dict = {}
        total_duration = 0
        total_overlap = 0
        uptime_hours = 0  # Initialize uptime_hours

        ignored_callsigns = [
            "OBS",
            "MTR",
            "ATIS",
            "INS",
            "ADM",
            "SUP"
        ]

        # Sort items by logon time
        items.sort(key=lambda item: item['logon_time'])

        for i in range(len(items)):
            item = items[i]
            self.logger.debug(f"Item: {item}")

            item_duration = float(item['duration']) / 60  # convert minutes to hours
            total_duration += item_duration

            self.logger.debug(f"Total duration: {total_duration}")

            # Replace double underscores with a single underscore
            cleaned_callsign = item['callsign'].replace("__", "_")

            callsign_parts = cleaned_callsign.split("_")
            if len(callsign_parts) == 3:  # Relief callsign

                # If callsign suffix is in the ignored_callsigns list, ignore it and move on to the next item
                if callsign_parts[2] in ignored_callsigns:
                    continue

                # Main callsign is the airport identifier + facility identifier
                main_callsign = f"{callsign_parts[0]}_{callsign_parts[2]}"  # Airport identifier + facility identifier
            else:  # Main callsign

                # If callsign suffix is in the ignored_callsigns list, ignore it and move on to the next item
                if callsign_parts[1] in ignored_callsigns:
                    continue

                main_callsign = cleaned_callsign

            relief_callsign = cleaned_callsign  # treat entire callsign as relief callsign

            if main_callsign not in callsigns:
                callsigns[main_callsign] = {'total_hours': 0, 'relief_callsigns': {}, 'overlap_hours': 0,
                                            'uptime_hours': 0}

            # Update total hours for main callsign
            callsigns[main_callsign]['total_hours'] += item_duration

            # Reduce precision of total_duration to 2 decimal places
            callsigns[main_callsign]['total_hours'] = float("{:.2f}".format(callsigns[main_callsign]['total_hours']))

            # Check for overlap
            if i < len(items) - 1:
                next_item = items[i + 1]
                item_logon_time = self.parse_date(item['logon_time'])
                next_item_logon_time = self.parse_date(next_item['logon_time'])
                if item_logon_time + timedelta(hours=item_duration) > next_item_logon_time:
                    overlap_duration = (item_logon_time + timedelta(
                        hours=float(
                            item_duration)) - next_item_logon_time).total_seconds() / 3600  # convert seconds to hours

                    non_overlap_duration = item_duration - overlap_duration  # Calculate non-overlapping part of item_duration
                    total_overlap += overlap_duration

                    callsigns[main_callsign]['overlap_hours'] += overlap_duration

                    # Reduce precision of overlap_duration to 2 decimal places
                    callsigns[main_callsign]['overlap_hours'] = float(
                        "{:.2f}".format(callsigns[main_callsign]['overlap_hours']))

                    # Update overlap hours for relief callsign
                    if relief_callsign in callsigns[main_callsign]['relief_callsigns']:
                        if 'overlap_hours' not in callsigns[main_callsign]['relief_callsigns'][relief_callsign]:
                            callsigns[main_callsign]['relief_callsigns'][relief_callsign]['overlap_hours'] = 0

                        callsigns[main_callsign]['relief_callsigns'][relief_callsign][
                            'overlap_hours'] += overlap_duration

                        # Reduce precision of overlap_hours to 2 decimal places
                        callsigns[main_callsign]['relief_callsigns'][relief_callsign]['overlap_hours'] = float(
                            "{:.2f}".format(
                                callsigns[main_callsign]['relief_callsigns'][relief_callsign]['overlap_hours']))

                        # Add non-overlapping part to uptime_hours for each callsign
                        #### MIDDLE
                        # Add non-overlapping part to uptime_hours for each callsign
                        callsigns[main_callsign]['uptime_hours'] += non_overlap_duration
                        if relief_callsign in callsigns[main_callsign]['relief_callsigns']:
                            callsigns[main_callsign]['relief_callsigns'][relief_callsign][
                                'uptime_hours'] += non_overlap_duration

                    else:
                        # if the next item's logon time is after the current item's session,
                        # then add the entire item_duration to uptime_hours
                        callsigns[main_callsign]['uptime_hours'] += item_duration

                        # Add item_duration to uptime_hours for each callsign
                        if relief_callsign in callsigns[main_callsign]['relief_callsigns']:
                            callsigns[main_callsign]['relief_callsigns'][relief_callsign][
                                'uptime_hours'] += item_duration

                else:
                    # If it's the last item, then add the entire item_duration to uptime_hours
                    callsigns[main_callsign]['uptime_hours'] += item_duration

                    # Add item_duration to uptime_hours for each callsign
                    if relief_callsign in callsigns[main_callsign]['relief_callsigns']:
                        callsigns[main_callsign]['relief_callsigns'][relief_callsign]['uptime_hours'] += item_duration

                # Add/update relief callsign
                if relief_callsign not in callsigns[main_callsign]['relief_callsigns']:
                    callsigns[main_callsign]['relief_callsigns'][relief_callsign] = {'hours': 0, 'uptime_hours': 0,
                                                                                     'overlap_hours': 0}

                callsigns[main_callsign]['relief_callsigns'][relief_callsign]['hours'] += item_duration

                # Reduce precision of hours to 2 decimal places
                callsigns[main_callsign]['relief_callsigns'][relief_callsign]['hours'] = float(
                    "{:.2f}".format(callsigns[main_callsign]['relief_callsigns'][relief_callsign]['hours']))

                ### END

        return callsigns, total_duration, total_overlap, uptime_hours

    def calculate_total_uptime_hours(self, callsigns):
        """
        Calculate total uptime hours for a given callsign
        :param callsigns:  dict
        :return:
        """
        total_uptime_hours = 0

        for callsign, data in callsigns.items():
            total_uptime_hours += data.get('uptime_hours', 0)
            for relief_data in data['relief_callsigns'].values():
                total_uptime_hours += relief_data.get('uptime_hours', 0)

        return total_uptime_hours

    def calculate_percentages(self, callsigns):
        self.logger.info(f"Calculating percentages...")
        total_hours_in_week = 24 * 7  # Total hours in a week
        sorted_callsigns = []

        for callsign, data in callsigns.items():
            # Round uptime_hours to 2 decimal places
            data['uptime_hours'] = float("{:.2f}".format(data['uptime_hours']))

            self.logger.debug(f"Calculating uptime percentage for {callsign}...")

            # Calculate uptime percentage
            uptime_percentage = round(data['uptime_hours'] / total_hours_in_week,
                                      5)  # Uptime percentage out of total hours in a week
            self.logger.debug(f"Uptime percentage: {uptime_percentage}")

            # Calculate overlap percentage
            relief_callsigns = []

            for relief_callsign, relief_data in data['relief_callsigns'].items():
                # Round uptime_hours to 2 decimal places
                relief_data['uptime_hours'] = float("{:.2f}".format(relief_data['uptime_hours']))

                self.logger.debug(f"Calculating uptime percentage for {relief_callsign}...")
                relief_uptime_percentage = round(relief_data['uptime_hours'] / total_hours_in_week,
                                                 5)  # Uptime percentage out of total hours in a week
                self.logger.debug(f"Uptime percentage: {relief_uptime_percentage}")

                relief_overlap_hours = relief_data.get('overlap_hours', 0)
                relief_callsigns.append((relief_callsign,
                                         {
                                             'uptime_hours': relief_data['uptime_hours'],
                                             'uptime_percentage': relief_uptime_percentage,
                                             'hours': relief_data['hours'],
                                             'overlap_hours': relief_overlap_hours
                                         }
                                         ))

            self.logger.debug(f"Completed calculating uptime percentages...")

            self.logger.debug(f"Sorting relief callsigns for {callsign}...")

            sorted_callsigns.append((callsign, {
                'uptime_hours': data['uptime_hours'],
                'uptime_percentage': uptime_percentage,
                'hours': data['total_hours'],
                'overlap_hours': data['overlap_hours'],
                'relief_callsigns': relief_callsigns
            }))

        self.logger.info(f"Sorting callsigns in descending order...")
        sorted_callsigns.sort(key=lambda x: x[1]['uptime_percentage'], reverse=True)

        self.logger.info(f"Completed calculating percentages...")
        return sorted_callsigns
