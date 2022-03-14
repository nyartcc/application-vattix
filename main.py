import argparse
import os.path
import random
import time
from sqlite3 import Error

from navdata.classes import Airport, Flight
from tools import db_init, calc_functions
import navdata.tools
from navdata.navdata import load_airac_data
from classes.vatsim_pilot import Pilot, Flightplan
import navdata

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
    parser.add_argument("-d", "--debug", help="(Optional) Set debug mode; sets certain parameters to default values "
                                              "and ignores live VATSIM data.", default=False, action='store_true')

    # Parse all the available
    args = parser.parse_args()

    verbose = args.verbose
    debug = args.debug

    # If the user specifies to load navdata (-n), run it!
    # FIXME Implement: Check if navadata already exist, if not return error requiring the user to input it.

    print("Loading data...")
    # Check if we're in production or not.
    if os.environ['env'] != 'prod':
        # Check if the dev db exists, if not, create one.
        if not os.path.isfile('dev.db'):
            if verbose:
                print("Database not found... Creating...")
            db, db_name = db_init.sql_connection()
            try:
                db_file = db_init.sql_table(db)
                if db_file is True and verbose is True:
                    print("Success! Created new file " + db_name)
                else:
                    if verbose:
                        print("Failed to create database... 😭 ", db_file[1])

                create_tables = navdata.tools.create_base_tables(db)
                if verbose:
                    print("Creating base tables...")
                if create_tables is True:
                    if verbose:
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
            if verbose:
                print("Database exists... Continue.")
            if args.navdata is not None:
                load_data = load_airac_data(args.navdata, args.verbose, args.skip)
                if load_data is True:
                    if verbose:
                        print("Success! Navdata loaded.")
                else:
                    print("❌ ERROR! Failed to load navdata...", load_data[1])
        con = db_init.connect_db("dev.db")

    print("Data loaded OK.")

    statusJson = get_vatsim_status()
    data = statusJson["v3"].pop()

    live_data, status = get_vatsim_data(args.verbose)

    if verbose:
        print("Data Status:" + status)

    print("------------------------------------------------------------------\n")

    pilot1 = live_data["pilots"][0]
    pilot2 = live_data["pilots"][1]
    i = 0

    for i, x in enumerate(live_data["pilots"]):
        pilot = Pilot.from_dict(x)

        if debug:
            # print(pilot)
            pass

        if pilot.flight_plan is not None:
            flight_plan = Flightplan.from_dict(pilot.flight_plan)

            pilot_dep_airport_coords = Airport.info(con, flight_plan.departure, "coordinates")
            pilot_arr_airport_coords = Airport.info(con, flight_plan.arrival, "coordinates")

            if pilot_dep_airport_coords and pilot_arr_airport_coords is not False:
                if debug:
                    print("🐛 Debug - pilot_arr/dep_airport_coords", pilot_arr_airport_coords, pilot_arr_airport_coords)

                dist_departure = round(calc_functions.distanceBetweenCoordinates(pilot_dep_airport_coords[0],
                                                                                 pilot_dep_airport_coords[1],
                                                                                 pilot.latitude,
                                                                                 pilot.longitude,
                                                                                 False, False))
                dist_arrival = round(calc_functions.distanceBetweenCoordinates(pilot_arr_airport_coords[0],
                                                                               pilot_arr_airport_coords[1],
                                                                               pilot.latitude,
                                                                               pilot.longitude,
                                                                               False, False))
                if debug:
                    print("🐛 Debug - dist_departure, dist_arrival:", dist_departure, dist_arrival)

                if dist_arrival < 10 and pilot.groundspeed < 50:
                    print(pilot.callsign, ": 🛬 Probably arrived at", flight_plan.arrival, "Distance from "
                                                                                           "arrival -",
                          dist_arrival)

                    # Insert into flights table
                    # id, connection_id, update_id, cid, latitude, longitude, altitude, groundspeed, transponder, heading, flight_plan, departed, departure_time, arrived, arrival_time, update_time

                    stuff = Flight(i, i, pilot.cid, pilot.latitude, pilot.longitude, pilot.altitude,
                                   pilot.groundspeed, pilot.transponder, pilot.heading, pilot.flight_plan,
                                   1, 2, time.time(), False, False)

                    thing = Flight.insert(stuff, con, stuff)


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

            if debug:
                print("i is:", i)
            if i == 10:
                break
            else:
                i += 1

        else:
            print(pilot.callsign, ": ❌ This pilot is a dumbass and flying without a flightplan. So... We're skipping "
                                  "him.")
