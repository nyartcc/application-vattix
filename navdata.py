import json
import os
from dataclasses import dataclass, field, asdict

import tools
from sqlite3 import Error


@dataclass
class Airport:
    icao: str = None
    name: str = None
    latitude: float = None
    longitude: float = None
    iata: str = None
    fir: str = None
    is_pseudo: int = 0
    id: int = field(default=None, compare=False)

    @classmethod
    def from_dict(cls, d):
        return Airport(**d)

    def to_dict(self):
        return asdict(self)


@dataclass
class Country:
    name: str = None
    code: str = None
    type: str = None
    id: int = field(default=None, compare=False)

    @classmethod
    def insert_country(cls):
        print(cls)




def loadAiracData(inputFile="VATSpy.json"):
    """
    Loads data from an input .json file and inserts it into the database.
    :param inputFile:
    :return: True, Number of inserted items, number of errored items, number of skipped items.
    """

    if not os.path.isfile(inputFile):
        raise FileNotFoundError(
            "The specified file \"{}\" does not exist. Please specify the correct filename.".format(inputFile))

    with open(inputFile) as data_file:
        dataJson = json.load(data_file)

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

        con = tools.connectDb(db)
        tools.createBaseTables(con)
    else:
        os.abort()

    totalInsert = 0
    totalFailed = 0
    totalSkip = 0

    # Loop through the VATSpy data JSON file.
    for x in dataJson:
        if x == "general":
            items = list(dataJson['general'].values())
            general = items[0], items[1], items[2]

            try:
                updateGeneral = tools.insertGeneral(con, general)
                if updateGeneral:
                    print("Inserted {}".format(general))
                else:
                    print("Updating general info failed!")
            except Error as e:
                print("Updating general info failed...", e)

            print(dataJson['general']['version'])

        if x == "countries":
            items = dataJson['countries'].items()

            insertCount = 0
            skipCount = 0
            failedCount = 0

            for i, y in items:
                # print("{} : {}".format(y["code"], y["name"]),
                # "{type}".format(type="({})".format(y["type"]) if y["type"] != "" else "")) # DEBUG

                check = tools.checkDuplicate(con, x, "code", y["code"])

                if check is False:
                    country = Country(y["name"], y["code"], y["type"])
                    try:
                        createCountry = tools.insertCountry(con, country)
                        print("{} {}".format(createCountry[2], country))
                        insertCount += 1
                    except Error as e:
                        print("Failed.", e)
                        failedCount += 1
                else:
                    # print("{} already exists in the database...".format(y["code"]))
                    skipCount += 1

            print("Countries --- Inserted: {} - Failed: {} - Skipped: {}".format(insertCount, failedCount,
                                                                                 skipCount))
            totalInsert += insertCount
            totalFailed += failedCount
            totalSkip += skipCount

        if x == "airports":
            items = dataJson['airports'].items()

            insertCount = 0
            skipCount = 0
            failedCount = 0

            for i, y in items:
                airport = Airport(y["icao"], y["name"], y["latitude"], y["longitude"], y["iata"], y["fir"], y["isPseudo"])
                print(airport)

                check = tools.checkDuplicate(con, x, "icao", y["icao"])
                if check is False:
                    try:
                        createAirport = tools.insertAirport(con, airport)
                        if createAirport:
                            insertCount += 1
                    except Error as e:
                        print("Failed to insert airport", e)
                        failedCount += 1
                else:
                    skipCount += 1

            print("Airports --- Inserted: {} - Failed: {} - Skipped: {}".format(insertCount, failedCount,
                                                                                skipCount))
            totalInsert += insertCount
            totalFailed += failedCount
            totalSkip += skipCount

    # Outside loop
    print("--------------")
    print("Total --- Inserted: {} - Failed: {} - Skipped: {}".format(totalInsert, totalFailed,
                                                                     totalSkip))

    # print(dataJson["general"])  # FIXME Debugging only


if __name__ == '__main__':
    loadAiracData("VATSpy.json")
