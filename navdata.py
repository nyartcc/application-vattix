import json
import os
import argparse
from classes import General, Country, Airport, Fir, Uir, Idl
import tools
from sqlite3 import Error


def load_airac_data(inputFile, verbose):
    """
    Loads data from an input .json file and inserts it into the database.
    :param inputFile:
    :param verbose: Set to TRUE to get extra debugging output
    :return: True, Number of inserted items, number of errored items, number of skipped items.
    """

    with open(inputFile) as data_file:
        data_json = json.load(data_file)

    if os.environ.get('env') is not None:
        environment = os.environ['env']
    else:
        environment = os.environ.get('env')

    # Check if we're in production or not.
    if environment != "prod":
        databaseFile = "dev.db"

        # Check if the dev db exists, if not, create one.
        if not os.path.isfile(databaseFile):
            # If there is no development database, this needs to be created first. Raise an alert to notify about this.
            raise FileNotFoundError("No database exits. Aborting.")
        else:
            print("Development database OK.")
            db = databaseFile

        con = tools.connect_db(db)
        tools.create_base_tables(con)
    else:
        print("You're in production. This application is not ready for that yet.")
        os.abort() # FIXME - Implement solution for production.

    total_insert = total_failed = total_skip = 0

    # Loop through the VATSpy data JSON file.
    for x in data_json:
        insert_count = skip_count = failed_count = 0
        items = data_json[x].items()

        if x == "general":
            items = list(data_json['general'].values())
            general = items[0], items[1], items[2]

            try:
                update_general = tools.insert_general(con, general)
                if update_general:
                    if verbose:
                        print("Inserted {}".format(general))
                else:
                    print("Updating general info failed!")
            except Error as e:
                print("Updating general info failed...", e)

            if verbose:
                print(data_json['general']['version'])

        if x == "countries":
            for i, y in items:
                # Verify if the item already exist
                check = tools.check_duplicate(con, x, "code", y["code"])

                if check is False:
                    country = Country(y["name"], y["code"], y["type"])
                    try:
                        create_country = tools.insert_country(con, country)
                        insert_count += 1
                        if verbose:
                            print("{} {}".format(create_country[2], country))
                    except Error as e:
                        print("Failed.", e)
                        failed_count += 1
                else:
                    if verbose is True:
                        print("{} already exists in the database...".format(y["code"]))
                    skip_count += 1

            # When done with this category, print a summary of what has been done
            print("Countries --- Inserted: {} - Failed: {} - Skipped: {}".format(insert_count, failed_count,
                                                                                 skip_count))

            # Add to the total counters of actions
            total_insert += insert_count
            total_failed += failed_count
            total_skip += skip_count

        if x == "airports":
            for i, y in items:

                airport = Airport(y["icao"], y["name"], y["latitude"], y["longitude"], y["iata"], y["fir"],
                                  y["isPseudo"])

                if verbose:
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
            pass

        if x == "uirs":
            pass

        if x == "idl":
            pass

    # Outside loop
    print("--------------")
    print("Total --- Inserted: {} - Failed: {} - Skipped: {}".format(total_insert, total_failed,
                                                                     total_skip))

    if verbose is True:
        print(data_json["general"])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # -f FILE
    parser.add_argument("-f", "--filename", help="The path to the input file", default="VATSpy.json")
    parser.add_argument("-v", "--verbose", help="(Optional) Add verbose debugging output",
                        default=False, action='store_true')
    args = parser.parse_args()

    if not args.filename:
        print("You must specify a filename with -f. Use --help for more info.")

    load_airac_data(args.filename, args.verbose)
