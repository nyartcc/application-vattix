from dataclasses import dataclass, field, asdict
from sqlite3 import Error


@dataclass
class General:
    version: str = None
    last_updated: int = None
    vatspy_data: str = None
    id: int = field(default=None, compare=False)


@dataclass
class Airport:
    icao: str = None
    name: str = None
    latitude: str = None
    longitude: str = None
    position: dict = None
    iata: str = None
    fir: str = None
    is_pseudo: int = 0
    id: int = field(default=None, compare=False)

    @classmethod
    def from_dict(cls, d):
        return Airport(**d)

    def to_dict(self):
        return asdict(self)

    def info(con, airport, info):
        """
         :param con:
         :param airport:
         :param info:
         :return:
         """

        cur = con.cursor()
        sql = "SELECT * FROM airports WHERE icao='{}'".format(airport)
        cur.execute(sql)
        row = cur.fetchone()

        if row is not None:
            airport = Airport(row[1], row[2], row[3], row[4], {"lat": row[3], "lon": row[4]}, row[5], row[6], row[7], row[8])

            if info == "coordinates":
                return airport.position
            else:
                print(airport)

        else:
            return False

    def cursor(self) -> object:
        """
        Get Pycharm to stop complaining.
        :return:
        """
        pass


@dataclass
class Country:
    name: str = None
    code: str = None
    type: str = None
    id: int = field(default=None, compare=False)

    @classmethod
    def insert_country(cls):
        print(cls)


@dataclass
class Fir:
    icao: str = None
    name: str = None
    callsign_prefix: str = None
    fir_boundary: str = None
    id: int = field(default=None, compare=False)


@dataclass
class Uir:
    prefix: str = None
    name: str = None
    coverage_firs: str = None
    id: int = field(default=None, compare=False)


@dataclass
class Idl:
    cord1: str = None
    cord2: str = None
    id: int = field(default=None, compare=False)


@dataclass
class Flight:
    connection_id: int
    update_id: int
    cid: int
    latitude: float
    longitude: float
    position: dict
    altitude: float
    groundspeed: float
    transponder: int
    heading: int
    flight_plan: dict
    departure_time: float
    arrival_time: float
    update_time: float
    departed: bool = field(default=False, compare=False)
    arrived: bool = field(default=False, compare=False)

    @classmethod
    def from_dict(cls, d):
        return Airport(**d)

    def to_dict(self):
        return asdict(self)

    def insert(self, con, flight):
        """

        :param flight:
        :param con:
        :return:
        """
        print(flight)

        sql = '''INSERT INTO flight_updates (connection_id, update_id, cid, latitude, longitude, altitude, groundspeed, 
        transponder, heading, flight_plan, departure_time, arrival_time, update_time, departed, arrived) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''

        try:
            cur = con.cursor()
            cur.execute(sql, flight.to_dict())
            con.commit()
            return True, cur.lastrowid
        except Error as e:
            print(e)
            return False, e
