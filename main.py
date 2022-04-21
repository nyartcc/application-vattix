import argparse
import logging
import os.path
import time
from sqlite3 import Error

from flights.models import FlightOld
from navdata.classes import Airport
from navdata.navdata import load_airac_data
from tools import db_init, calc_functions
import navdata.tools
from classes.vatsim_pilot import Pilot, Flightplan
from vatsim_data.vatsim_data import get_vatsim_data, get_vatsim_status

global DEBUG
global VERBOSE
global NUMBER_OF_PILOTS

# Get commandline arguments that the user may input to customize the application.
parser = argparse.ArgumentParser()

# Specify the arguments available to the user
parser.add_argument("-n", "--navdata", help="The path to the navdata input file")
parser.add_argument("-s", "--skip", help="(Optional) Pass in a JSON object in the navdata JSON file to be "
                                         "skipped to save DEBUG time")
parser.add_argument("-v", "--verbose", help="(Optional) Add VERBOSE debugging output",
                    default=False, action='store_true')
parser.add_argument("-d", "--debug", help="(Optional) Set DEBUG mode; sets certain parameters to default values "
                                          "and ignores live VATSIM data.", default=False, action='store_true')

# Parse all the available
args = parser.parse_args()

NUMBER_OF_PILOTS = 0
VERBOSE = os.environ.get('VERBOSE', False)
DEBUG = os.environ.get('DEBUG', False)


def main():
    # FIXME Implement: Check if navadata already exist, if not return error requiring the user to input it.

    logging.info("Loading data...")
    # Check if we're in production or not.
    if os.environ.get('ENV') != 'prod':
        # Check if the dev db exists, if not, create one.
        if not os.path.isfile('dev.db'):
            logging.warning("Database not found... Creating...")
            db, db_name = db_init.connect_db('dev.db')
            try:
                db_file = db_init.sql_table(db)
                if db_file is True:
                    logging.debug("Success! Created new file " + db_name)
                else:
                    logging.error("Failed to create database... 😭 ", db_file)

                create_tables = navdata.tools.create_base_tables(db)

                logging.info("Creating Base tables...")

                if create_tables is True:
                    logging.debug("Success! Tables created successfully! 🎉 ")
                else:
                    logging.error("❌ ERROR! Failed to create Base tables.")
            except Error as e:
                logging.error(e)
                os.abort()

            logging.debug("Loading navdata...")

            if args.navdata is not None:
                load_data = load_airac_data(args.navdata, args.skip)
                if load_data is True:
                    logging.debug("🎉 Success! Navdata loaded.")
                else:
                    logging.error("❌ ERROR! Failed to load navdata...", load_data[1])
            else:
                logging.error("❌ ERROR! We're required to load base navdata. Please specify the location "
                              "of the navdata JSON file using the -n flag. Need help? Use --help!")
                os.remove(db_name)
                logging.error("⚠️ Aborting! Deleted file " + db_name)
                os.abort()

        else:
            logging.debug("Database exists... Continue.")
            if args.navdata is not None:
                load_data = load_airac_data(args.navdata, args.skip)
                if load_data is True:
                    logging.debug("Success! Navdata loaded.")
                else:
                    logging.error("❌ ERROR! Failed to load navdata...", load_data[1])
        con = db_init.connect_db("dev.db")
        con = con.cursor()

    logging.debug("Data loaded OK.")

    statusJson = get_vatsim_status()
    data = statusJson["v3"].pop()

    live_data, status = get_vatsim_data()

    logging.debug("Data Status:" + status)

    NUMBER_OF_PILOTS = len(live_data["pilots"])

    for i, x in enumerate(live_data["pilots"]):
        # Create a single position value based on the lat, lon of the pilots position for easy reference.
        # Append it to the existing dict.
        x["position"] = {
            "lat": x["latitude"],
            "lon": x["longitude"]
        }

        # Turn the dictionary into an object
        pilot = Pilot.from_dict(x)

        print("🐛 Debug - pilot:", pilot)

        # FIXME, for now, only deal with pilots that have a flightplan
        if pilot.flight_plan is not None:
            flight_plan = Flightplan.from_dict(pilot.flight_plan)

            pilot_dep_airport_coords = Airport.info(con, flight_plan.departure, "coordinates")
            pilot_arr_airport_coords = Airport.info(con, flight_plan.arrival, "coordinates")

            print("🐛 Debug - pilot_arr/dep_airport_coords", pilot_arr_airport_coords, pilot_dep_airport_coords)

            if pilot_dep_airport_coords and pilot_arr_airport_coords is not False:

                dist_departure = round(
                    calc_functions.distance_between_coordinates(pilot_dep_airport_coords, pilot.position))
                dist_arrival = round(
                    calc_functions.distance_between_coordinates(pilot_arr_airport_coords, pilot.position))

                if dist_arrival < 10 and pilot.groundspeed < 50:
                    print(pilot.callsign, ": 🛬 Probably arrived at", flight_plan.arrival, "Distance from "
                                                                                           "arrival -",
                          dist_arrival)

                    # FIXME Insert into flight_updates table - Temp variable name
                    stuff = FlightOld(i, i, pilot.cid, pilot.latitude, pilot.longitude, pilot.position,
                                      pilot.altitude, pilot.groundspeed, pilot.transponder, pilot.heading,
                                      pilot.flight_plan, 1, 2, time.time(), False, False)

                    thing = FlightOld.insert(stuff, con, stuff)
                    if thing[0] is not True:
                        logging.error("Failed to insert into database")

                elif dist_departure < 10 and pilot.groundspeed < 50:
                    print(pilot.callsign, ": 🛫 Probably not departed from", flight_plan.departure, "yet... Distance "
                                                                                                    "from departure "
                                                                                                    "-",
                          dist_departure)
                elif pilot.groundspeed >= 50:
                    print(pilot.callsign, ": 🛩 In flight. Distance from arrival -", dist_arrival, "Altitude:",
                          pilot.altitude)
            else:
                if pilot_dep_airport_coords is False:
                    print(pilot.callsign, ": ⚠️ Departure airport not found in navdata. Unable to continue.")
                elif pilot_arr_airport_coords is False:
                    print(pilot.callsign, ": ⚠️ Arrival airport not found in navdata. Unable to continue.")

            # Todo: Calculate distance a pilot has travelled since the last update.
            # Need to check their current position against the last position.
            # Also need to check distance from origin and destination.

        else:  # FIXME - pilot has no flightplan
            print(pilot.callsign, ": ❌ This pilot is a dumbass and flying without a flightplan. So... We're skipping "
                                  "him.")

    logging.info("\n-------- DEBUG --------")
    logging.info("| # pilots: {}".format(NUMBER_OF_PILOTS))


if __name__ == '__main__':
    level = logging.INFO
    fmt = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=level, format=fmt)

    main()
