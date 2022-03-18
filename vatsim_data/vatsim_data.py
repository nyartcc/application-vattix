import json, pytz
from datetime import date, datetime
from urllib.request import urlopen


def get_vatsim_status():

    statusUrl = urlopen('https://status.vatsim.net/status.json')
    statusJson = json.loads(statusUrl.read())

    return statusJson["data"]


def get_vatsim_data():
    from main import debug, verbose

    # To avoid abusing the data servers, we want to first check the cached data if it is out of date.
    # Open the cached data file - FIXME Replace with database instead of local file
    global status, data_last_update
    try:  # FIXME THIS ENTIRE THING IS GARBAGE
        with open('../vatsim_live_data.json') as data_file:
            data_json = json.load(data_file)
            status = "cached"
    except:
        data_json = {
            "general": {
                "update": "0"
            }}

    # Get the current time in UTC
    time_now = datetime.now(pytz.utc)
    time_stamp = time_now.strftime("%Y%m%d%H%M%S")
    if verbose is True:
        print("TIMESTAMP:" + time_stamp)

    # Check the cached data when it was last updated
    try:
        data_last_update = data_json["general"]["update"]
    except ValueError as err:
        result = err
    if verbose is True:
        print("CURRENT DATA TIME:" + data_last_update)

    # Compare the difference between the cached data and local time
    data_time_difference = int(time_stamp) - int(data_last_update)
    if verbose is True:
        print("Current diff: " + str(data_time_difference))

    # The data is stale - it has been more than 90 seconds since the last update
    if data_time_difference > 90:

        print("Getting new data from VATSIM...")
        vatsim_status = get_vatsim_status()
        dataUrl = vatsim_status["v3"].pop()
        dataUrl = urlopen(dataUrl)
        data_json = json.loads(dataUrl.read())
        print("Data loaded OK...")

        new_data_update_time = data_json["general"]["update"]
        if verbose is True:
            print("New update time:" + new_data_update_time)

        if data_last_update != new_data_update_time:
            # Cache the data locally
            with open('../vatsim_live_data.json', 'w') as outfile:
                json.dump(data_json, outfile)
        else:
            print("Data is up to date.")

        status = "updated"

    return data_json, status
