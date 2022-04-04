import json
import os
import argparse

import requests

from navdata.classes import Country, Airport, Fir, Uir, Idl
import navdata.tools as tools
from sqlite3 import Error

DEBUG = False
VERBOSE = False


def load_airac_data(inputFile, skip):
    """
    Loads data from an input .json file and inserts it into the database.
    :param inputFile:
    :return: True, Number of inserted items, number of errored items, number of skipped items.
    """

    with open(inputFile) as data_file:
        data_json = json.load(data_file)

    # Mumbo jumbo to ensure environment variables are initialized properly.
    # If none are set, assume we're in dev.
    if os.environ.get('ENV') is not None:
        environment = os.environ['ENV']
    else:
        environment = os.environ.get('ENV')

    # Check if we're in development or not.
    if environment != "prod":
        # Use a local sqlite database file
        databaseFile = "dev.db"

        # Check if the dev db file exists, if not, create one.
        if not os.path.isfile(databaseFile):
            # If there is no development database, this needs to be created first. Raise an alert to notify about this.
            raise FileNotFoundError("No database exits. Aborting.")
        else:
            print("Development database OK.")
            db = databaseFile

        con = tools.connect_db(db)
        tools.create_base_tables(con)
    else:
        print("You're in production. This application is not ready for that yet. Sowwy...")
        os.abort()  # FIXME - Implement solution for production.

    total_insert = total_failed = total_skip = 0

    # Loop through the VATSpy data JSON file.
    for x in data_json:
        insert_count = skip_count = failed_count = 0
        items = data_json[x].items()

        if x == "general" and skip != "countries":
            items = list(data_json['general'].values())
            general = items[0], items[1], items[2]

            try:
                update_general = tools.insert_general(con, general)
                if update_general:
                    if VERBOSE:
                        print("Inserted {}".format(general))
                else:
                    print("Updating general info failed!")
            except Error as e:
                print("Updating general info failed...", e)

            if VERBOSE:
                print(data_json['general']['version'])

        if x == "countries" and skip != "countries":
            for i, y in items:
                # Verify if the item already exist
                check = tools.check_duplicate(con, x, "code", y["code"])

                if check is False:
                    country = Country(y["name"], y["code"], y["type"])
                    try:
                        create_country = tools.insert_country(con, country)
                        insert_count += 1
                        if VERBOSE:
                            print("{}".format(create_country[2]))
                    except Error as e:
                        print("Failed.", e)
                        failed_count += 1
                else:
                    if VERBOSE is True:
                        print("{} already exists in the database...".format(y["code"]))
                    skip_count += 1

            # When done with this category, print a summary of what has been done
            print("Countries --- Inserted: {} - Failed: {} - Skipped: {}".format(insert_count, failed_count,
                                                                                 skip_count))

            # Add to the total counters of actions
            total_insert += insert_count
            total_failed += failed_count
            total_skip += skip_count

        if x == "airports" and skip != "airports":
            for i, y in items:

                airport = Airport(y["icao"], y["name"], y["latitude"], y["longitude"], y["iata"], y["fir"],
                                  y["isPseudo"])

                if VERBOSE:
                    print(airport)

                check = tools.check_duplicate(con, x, "icao", y["icao"])
                if check is False:
                    try:
                        create_airport = tools.insert_airport(con, airport)
                        print(create_airport)
                        if create_airport:
                            insert_count += 1

                    except Error as e:
                        print("Failed to insert airport", e)
                        failed_count += 1
                else:
                    skip_count += 1

            # When done with this category, print a summary of what has been done
            print("Airports --- Inserted: {} - Failed: {} - Skipped: {}".format(insert_count, failed_count,
                                                                                skip_count))
            # Add to the total counters of actions
            total_insert += insert_count
            total_failed += failed_count
            total_skip += skip_count

        if x == "firs":
            for i, y in items:
                fir = Fir(y["icao"], y["name"], y["callsignPrefix"], y["firBoundary"])
                if VERBOSE:
                    print(fir)

                check = tools.check_duplicate(con, x, "icao", fir.icao)
                if check is False:
                    try:
                        create_fir = tools.insert_fir(con, fir)
                        if VERBOSE:
                            print(create_fir)
                        if create_fir:
                            insert_count += 1
                    except Error as e:
                        print("Failed to create FIR", e)
                        failed_count += 1
                else:
                    skip_count += 1
                    if VERBOSE:
                        print("Skipped FIR {}".format(fir.icao))

            # When done with this category, print a summary of what has been done
            print("FIRs --- Inserted: {} - Failed: {} - Skipped: {}".format(insert_count, failed_count,
                                                                            skip_count))
            # Add to the total counters of actions
            total_insert += insert_count
            total_failed += failed_count
            total_skip += skip_count

        if x == "uirs":
            for i, y in items:
                uir = Uir(y["prefix"], y["name"], y["coverageFirs"])
                if VERBOSE:
                    print(uir)

                check = tools.check_duplicate(con, x, "name", uir.name)
                if check is False:
                    try:
                        create_uir = tools.insert_uir(con, uir)
                        if VERBOSE:
                            print(create_uir)
                        if create_uir:
                            insert_count += 1
                    except Error as e:
                        print("Failed to create UIR", e)
                        failed_count += 1
                else:
                    skip_count += 1
                    if VERBOSE:
                        print("Skipped UIR {}".format(uir.name))

            # When done with this category, print a summary of what has been done
            print("UIRs --- Inserted: {} - Failed: {} - Skipped: {}".format(insert_count, failed_count,
                                                                            skip_count))
            # Add to the total counters of actions
            total_insert += insert_count
            total_failed += failed_count
            total_skip += skip_count

        if x == "idl":

            drop_idl = tools.delete_idl(con)
            if drop_idl:
                print("Successfully dropped previous IDL")

                for i, y in items:
                    idl = Idl(y["cord1"], y["cord2"])
                    if VERBOSE:
                        print(idl)

                    try:
                        create_idl = tools.insert_idl(con, idl)
                        if VERBOSE:
                            print(create_idl)
                        if create_idl:
                            insert_count += 1
                    except Error as e:
                        print("Failed to create IDL", e)
                        failed_count += 1

            # When done with this category, print a summary of what has been done
            print("IDL --- Inserted: {} - Failed: {}".format(insert_count, failed_count))
            # Add to the total counters of actions
            total_insert += insert_count
            total_failed += failed_count

    # Outside loop
    print("--------------")
    print("Total --- Inserted: {} - Failed: {} - Skipped: {}".format(total_insert, total_failed,
                                                                     total_skip))

    if VERBOSE is True:
        print(data_json["general"])

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # -f FILE
    parser.add_argument("-f", "--filename", help="The path to the input file", default="navdata/VATSpy.json")
    parser.add_argument("-s", "--skip", help="(Optional) Pass in a JSON object to be skipped to save DEBUG time")
    args = parser.parse_args()

    if not args.filename:
        print("You must specify a filename with -f. Use --help for more info.")

    load_airac_data(args.filename, args.skip)
