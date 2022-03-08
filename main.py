import argparse
import os.path
import db_init
import calc_functions

from vatsim_data import get_vatsim_data, get_vatsim_status

if __name__ == '__main__':

    # Check if we're in production or not.
    if os.environ['env'] != 'prod':
        # Check if the dev db exists, if not, create one.
        if not os.path.isfile('dev.db'):
            db, db_name = db_init.sql_connection()
            db_init.sql_table(db)
            print("Database did not exist. Created new file " + db_name)
        else:
            print("Database exists... Continue.")

    statusJson = get_vatsim_status()
    data = statusJson["v3"].pop()

    parser = argparse.ArgumentParser()

    # Add ability for better debugging with argparser
    parser.add_argument("-v", "--verbose", help="(Optional) Add verbose debugging output",
                        default=False, action='store_true')
    args = parser.parse_args()

    live_data, status = get_vatsim_data(args.verbose)

    print("Data Status:" + status)

    pilot1 = live_data["pilots"][0]
    pilot2 = live_data["pilots"][1]

    d = calc_functions.distanceBetweenCoordinates(pilot1["latitude"], pilot1["longitude"],
                                                  pilot2["latitude"], pilot2["longitude"])

    # Todo: Calculate distance a pilot has travelled since the last update.
    # Need to check their current position against the last position.
    # Also need to check distance from origin and destination.

    s = "The distance between {} and {} is {} nautical miles".format(pilot1["callsign"], pilot2["callsign"], round(d))
    print(s)
