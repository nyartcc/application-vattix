import json, pytz
from datetime import date, datetime
from urllib.request import urlopen


def getVatsimStatus():
    statusUrl = urlopen('https://status.vatsim.net/status.json')
    statusJson = json.loads(statusUrl.read())

    return statusJson["data"]


def getVatsimData():
    # To avoid abusing the data servers, we want to first check the cached data if it is out of date.
    # Open the cached data file - FIXME Replace with database instead of local file
    global status
    try:
        with open('vatsim_live_data.json') as data_file:
            dataJson = json.load(data_file)
            status = "cached"
    except:
        dataJson = {
            "general": {
                "update": "0"
            }}

    # Get the current time in UTC
    time_now = datetime.now(pytz.utc)
    time_stamp = time_now.strftime("%Y%m%d%H%M%S")
    print("TIMESTAMP:" + time_stamp)  # FIXME Debug only

    # Check the cached data when it was last updated
    try:
        dataLastUpdate = dataJson["general"]["update"]
    except ValueError as err:
        result = err
    print("CURRENT DATA TIME:" + dataLastUpdate)  # FIXME Debug Only

    # Compare the difference between the cached data and local time
    dataTimeDifference = int(time_stamp) - int(dataLastUpdate)
    print("Current diff: " + str(dataTimeDifference))

    # The data is stale - it has been more than 90 seconds since the last update
    if dataTimeDifference > 90:

        print("Getting new data from VATSIM...")
        vatsimStatus = getVatsimStatus()
        dataUrl = vatsimStatus["v3"].pop()
        dataUrl = urlopen(dataUrl)
        dataJson = json.loads(dataUrl.read())

        newDataUpdateTime = dataJson["general"]["update"]
        print("New update time:" + newDataUpdateTime)

        if dataLastUpdate != newDataUpdateTime:
            # Cache the data locally
            with open('vatsim_live_data.json', 'w') as outfile:
                json.dump(dataJson, outfile)
        else:
            print("Data is up to date.")

        status = "updated"

    return dataJson, status
