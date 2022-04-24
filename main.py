import argparse
import logging
import os.path
import time
from sqlite3 import Error

from flask import Flask
from sqlalchemy import update

import flights.models
from flights.crud import Base, engine, Session
from flights.models import FlightOld, Flights
from navdata.classes import Airport
from navdata.navdata import load_airac_data
from tools import db_init, calc_functions
import navdata.tools
from classes.vatsim_pilot import Pilot, Flightplan
from vatsim_data.vatsim_data import get_vatsim_data, get_vatsim_status

global DEBUG
global VERBOSE
global NUMBER_OF_PILOTS

NUMBER_OF_PILOTS = 0
VERBOSE = os.environ.get('VERBOSE', False)
DEBUG = os.environ.get('DEBUG', False)


def create_db():
    """
    Creates the database and returns the name of the database.
    """
    db, db_name = db_init.connect_db('dev.db')
    try:
        db_file = db_init.sql_table(db)
        if db_file is True:
            logging.debug(f"Success! Created new file {db_name}")
        else:
            logging.error(f"Failed to create database... 😭 {db_file}")

        create_tables = navdata.tools.create_base_tables(db)

        logging.info("Creating Base tables...")

        if create_tables is True:
            logging.info("Success! Tables created successfully! 🎉 ")
        else:
            logging.error("❌ ERROR! Failed to create Base tables.")
    except Error as e:
        logging.error(e)
        os.abort()

    return db_name


def check_database():
    """
    Checks if the database exists.
    """

    logging.info("Loading data...")
    # Check if we're in production or not.
    if os.environ.get('ENV') != 'prod':
        # Check if the dev db exists, if not, create one.
        if not os.path.isfile('dev.db'):
            logging.warning("Database not found... Creating...")

            db_name = create_db()  # Since no DB exist, create one.

            logging.debug("Loading navdata...")

            if args.navdata is not None:
                load_data = load_airac_data(args.navdata, args.skip)
                if load_data is True:
                    logging.debug("🎉 Success! Navdata loaded.")
                else:
                    logging.error(f"❌ ERROR! Failed to load navdata... {load_data[1]}")
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
                    logging.error(f"❌ ERROR! Failed to load navdata... {load_data[1]}")


def insert_flight(session, flight, flight_plan):
    """
    Inserts a new flight into the database.
    """
    # Insert the flight into the database.

    flight_obj = flight

    # Insert the flight plan into the database.
    flight_fp = flight_plan

    flight.flight_plan = [flight_fp]

    session.add(flight_fp)
    session.add(flight_obj)
    session.commit()
    logging.debug("Added")  # Log that we've added the flight.


def update_flight(session, flight_position):
    """
    Updates the flight position.
    """
    flight_position_obj = flight_position

    session.add(flight_position_obj)
    session.commit()
    logging.debug("Updated")  # Log that we've updated the flight.


def main():
    """
    Main function.
    """
    tic = time.perf_counter()  # Start a performance counter to see how long the application takes to run.

    check_database()  # Verify that we have a database connection

    # Establish a database connection to the dev database.
    con = db_init.connect_db("dev.db")
    con = con.cursor()
    logging.debug("Data loaded OK.")

    live_data, status = get_vatsim_data()  # Get pilot data from VATSIM

    logging.debug("Data Status:" + status)

    Base.metadata.create_all(engine)  # Create the base tables.
    session = Session()  # Create a database session.

    NUMBER_OF_PILOTS: int = len(live_data["pilots"])  # Get the total number of pilots. Only used for logging.

    # If we have live data, process it.
    if NUMBER_OF_PILOTS > 0:  # FIXME - DISABLED FOR DEBUGGING
        for i, x in enumerate(live_data["pilots"]):

            # Create a single position value based on the lat, lon of the pilots position for easy reference.
            # Append it to the existing dict.
            x["position"] = {
                "lat": x["latitude"],
                "lon": x["longitude"]
            }

            pilot = Pilot.from_dict(x)  # Turn the dictionary into an object

            if pilot.flight_plan is not None:  # Check if the pilot has a flightplan or not.
                flight_plan = Flightplan.from_dict(
                    pilot.flight_plan)  # Convert the flightplan into a Flightplan object.

                timestamp = time.time()  # Get the current time.

                # Check if the flight already exists in the database.
                exists = session.query(Flights).filter_by(callsign=pilot.callsign, cid=pilot.cid).order_by(
                    Flights.timestamp.desc()).first()

                if exists is not None:
                    delta = timestamp - exists.timestamp  # Calculate the difference between the current time and the
                    # last time.
                else:
                    delta = 600  # Dirty hack, but if the flight doesn't exist, force the delta to be higher.

                if delta >= 600:  # If the difference is greater than 10 minutes, generate a new flight

                    pilot_dep_airport_coords = Airport.info(con, flight_plan.departure, "coordinates")  # Departure airport coordinates
                    pilot_arr_airport_coords = Airport.info(con, flight_plan.arrival, "coordinates")  # Arrival airport coordinates

                    if pilot_dep_airport_coords and pilot_arr_airport_coords is not False:  # Check if the airport exists in the DB
                        pilot_departed = False
                        pilot_arrived = False

                        dist_departure = round(
                            calc_functions.distance_between_coordinates(pilot_dep_airport_coords, pilot.position))
                        dist_arrival = round(
                            calc_functions.distance_between_coordinates(pilot_arr_airport_coords, pilot.position))

                        if dist_arrival < 8 and pilot.groundspeed < 50:
                            logging.debug(
                                f"{pilot.callsign}: 🛬 Probably arrived at {flight_plan.arrival} "
                                f"Distance from arrival - {dist_arrival}")
                            pilot_arrived = True
                        elif dist_departure < 8 and pilot.groundspeed < 50:
                            logging.debug(
                                f"{pilot.callsign}: 🛫 Probably not departed from {flight_plan.departure} yet... "
                                f"Distance from departure - {dist_departure}")
                            pilot_departed = False
                        elif pilot.groundspeed >= 50 and dist_departure >= 8:
                            logging.debug(
                                f"{pilot.callsign}: 🛩 In flight. Distance from arrival - {dist_arrival} Altitude: "
                                f"{pilot.altitude}")
                            pilot_departed = True
                        else:
                            logging.debug(f"{pilot.callsign}: ❓ Unknown. Pilot has groundspeed of {pilot.groundspeed} "
                                          f"and altitude of {pilot.altitude}")

                        # Create a new flight in the database.
                        insert_flight(session,
                                      Flights(pilot.callsign, pilot.cid, pilot_departed, pilot_arrived, timestamp),
                                      flights.models.FlightPlan(flight_rules=flight_plan.flight_rules,
                                                                aircraft=flight_plan.aircraft,
                                                                aircraft_faa=flight_plan.aircraft_faa,
                                                                aircraft_short=flight_plan.aircraft_short,
                                                                departure_airport=flight_plan.departure,
                                                                arrival_airport=flight_plan.arrival,
                                                                alternate_airport=flight_plan.alternate,
                                                                cruise_tas=flight_plan.cruise_tas,
                                                                altitude=flight_plan.altitude,
                                                                deptime=flight_plan.deptime,
                                                                enroute_time=flight_plan.enroute_time,
                                                                fuel_time=flight_plan.fuel_time,
                                                                remarks=flight_plan.remarks,
                                                                route=flight_plan.route,
                                                                revision_id=flight_plan.revision_id,
                                                                assigned_transponder=flight_plan.assigned_transponder
                                                                )
                                      )

                        # Also create a flight position update for the current position.
                        update_flight(session,
                                      flights.models.FlightUpdate(cid=pilot.cid,
                                                                  callsign=pilot.callsign,
                                                                  latitude=pilot.latitude,
                                                                  longitude=pilot.longitude,
                                                                  altitude=pilot.altitude,
                                                                  groundspeed=pilot.groundspeed,
                                                                  heading=pilot.heading,
                                                                  transponder=pilot.transponder,
                                                                  flight_plan=str(pilot.flight_plan),
                                                                  logon_time=pilot.logon_time,
                                                                  last_updated=pilot.last_updated,
                                                                  timestamp=timestamp,
                                                                  flight=exists))
                    else:
                        if pilot_dep_airport_coords is False:
                            logging.warning(
                                f"{pilot.callsign}:️ Departure airport ({flight_plan.departure}) not found in navdata.")
                        elif pilot_arr_airport_coords is False:
                            logging.warning(
                                f"{pilot.callsign}:️ Arrival airport ({flight_plan.arrival}) not found in navdata.")

                    # Todo: Calculate distance a pilot has travelled since the last update.
                    # Need to check their current position against the last position.
                    # Also need to check distance from origin and destination.

                # If the difference is less than 5 minutes, post a flight update
                else:
                    update_flight(session,
                                  flights.models.FlightUpdate(cid=pilot.cid,
                                                              callsign=pilot.callsign,
                                                              latitude=pilot.latitude,
                                                              longitude=pilot.longitude,
                                                              altitude=pilot.altitude,
                                                              groundspeed=pilot.groundspeed,
                                                              heading=pilot.heading,
                                                              transponder=pilot.transponder,
                                                              flight_plan=str(pilot.flight_plan),
                                                              logon_time=pilot.logon_time,
                                                              last_updated=pilot.last_updated,
                                                              timestamp=timestamp,
                                                              flight=exists))

            else:  # FIXME - pilot has no flightplan
                logging.debug(
                    f"{pilot.callsign}: ❌ This pilot is a dumbass and flying without a flightplan. So... We're "
                    f"skipping him.")

    logging.info("\n-------- INFO --------")
    logging.info("| # pilots: {}".format(NUMBER_OF_PILOTS))

    toc = time.perf_counter()
    logging.info(f"Application time: {toc - tic:0.4f} seconds")


if __name__ == '__main__':
    level = logging.INFO
    fmt = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=level, format=fmt)

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

    main()
