import argparse
import os.path
from sqlite3 import Error

from tools import db_init, calc_functions
import navdata.tools
from navdata.navdata import load_airac_data

from vatsim_data.vatsim_data import get_vatsim_data, get_vatsim_status

if __name__ == '__main__':

    # Get commandline arguments that the user may input to customize the application.
    parser = argparse.ArgumentParser()

    # Specify the arguments available to the user
    parser.add_argument("-n", "--navdata", help="The path to the navdata input file")
    parser.add_argument("-s", "--skip", help="(Optional) Pass in a JSON object in the navdata JSON file to be "
                                             "skipped to save debug time")
    parser.add_argument("-v", "--verbose", help="(Optional) Add verbose debugging output",
                        default=False, action='store_true')

    # Parse all the available
    args = parser.parse_args()

    # If the user specifies to load navdata (-n), run it!
     # FIXME Implement: Check if navadata already exist, if not return error requiring the user to input it.

    print(args.navdata)
    # Check if we're in production or not.
    if os.environ['env'] != 'prod':
        # Check if the dev db exists, if not, create one.
        if not os.path.isfile('dev.db'):
            print("Database not found... Creating...")
            db, db_name = db_init.sql_connection()
            try:
                db_file = db_init.sql_table(db)
                if db_file is True:
                    print("Success! Created new file " + db_name)
                else:
                    print("Failed to create database... 😭 ", db_file[1])

                create_tables = navdata.tools.create_base_tables(db)
                print("Creating base tables...")
                if create_tables is True:
                    print("Success! Tables created successfully! 🎉 ")
                else:
                    print("❌ ERROR! Failed to create base tables.")
            except Error as e:
                print(e)
                os.abort()

            print("Loading navdata...")
            if args.navdata is not None:
                load_data = load_airac_data(args.navdata, args.verbose, args.skip)
                if load_data is True:
                    print("🎉 Success! Navdata loaded.")
                else:
                    print("❌ ERROR! Failed to load navdata...", load_data[1])
            else:
                print("❌ ERROR! We're required to load base navdata. Please specify the location of the navdata JSON "
                      "file using the -n flag. Need help? Use --help!")
                os.remove(db_name)
                print("⚠️ Aborting! Deleted file " + db_name)
                os.abort()

        else:
            print("Database exists... Continue.")
            if args.navdata is not None:
                load_data = load_airac_data(args.navdata, args.verbose, args.skip)
                if load_data is True:
                    print("Success! Navdata loaded.")
                else:
                    print("❌ ERROR! Failed to load navdata...", load_data[1])

    statusJson = get_vatsim_status()
    data = statusJson["v3"].pop()

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
