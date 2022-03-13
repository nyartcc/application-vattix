from dataclasses import dataclass, field, asdict


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
            airport = Airport(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])

            if info == "coordinates":
                return [airport.latitude, airport.longitude]
            else:
                print(airport)

        else:
            return False

    def cursor(self):
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
