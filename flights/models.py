from dataclasses import field, dataclass, asdict
from sqlite3 import Error

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Flights(Base):
    __tablename__ = 'flights'
    id = Column(Integer, primary_key=True)
    callsign = Column(String, nullable=False)
    flight_plan = Column(Integer, ForeignKey('flight_plans.id'))
    departed = Column(Boolean, nullable=False)
    arrived = Column(Boolean, nullable=False)

    def __repr__(self):
        return f'<Flights(id={self.id}, callsign={self.callsign}, flight_plan={self.flight_plan}, ' \
               f'departed={self.departed}, arrived={self.arrived})>'


class FlightPlan(Base):
    __tablename__ = 'flight_plans'
    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer)
    flight_rules = Column(String)
    aircraft = Column(String)
    aircraft_faa = Column(String)
    aircraft_short = Column(String)
    departure_airport = Column(String)
    arrival_airport = Column(String)
    alternate_airport = Column(String)
    cruise_tas = Column(Float)
    altitude = Column(Float)
    deptime = Column(Integer)
    enroute_time = Column(Integer)
    fuel_time = Column(Integer)
    remarks = Column(String)
    route = Column(String)
    revision_id = Column(Integer)
    assigned_transponder = Column(Integer)


class FlightUpdate(Base):
    __tablename__ = 'flight_updates'
    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey('flights.id'))
    cid = Column(Integer)
    callsign = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    groundspeed = Column(Float)
    heading = Column(Float)
    transponder = Column(Integer)
    flight_plan = Column(Integer, ForeignKey('flight_plans.id'))
    logon_time = Column(Integer)
    last_updated = Column(Integer)
    timestamp = Column(Integer)


@dataclass
class FlightOld:
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
    def from_dict(cls, d):  # pragma: no cover
        pass

    def to_dict(self):  # pragma: no cover
        return asdict(self)

    def insert(self, con, flight):  # pragma: no cover
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
            con.execute(sql, flight.to_dict())
            con.commit()
            return True, con.lastrowid
        except Error as e:
            print(e)
            return False, e
