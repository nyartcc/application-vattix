from dataclasses import field, dataclass, asdict
from sqlite3 import Error

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from flights.crud import Base


@dataclass
class Flights(Base):
    __tablename__ = 'flights'
    id = Column(Integer, primary_key=True)
    callsign = Column(String, nullable=False)
    cid = Column(Integer, nullable=False)
    departed = Column(Boolean, nullable=False)
    arrived = Column(Boolean, nullable=False)
    timestamp = Column(Float, nullable=False)
    flight_plan = relationship("FlightPlan", back_populates="flight")
    flight_update = relationship("FlightUpdate", back_populates="flight")

    def __init__(self, callsign, cid, departed, arrived, timestamp):
        self.callsign = callsign
        self.cid = cid
        self.departed = departed
        self.arrived = arrived
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.callsign, self.cid, self.departed, self.arrived, self.timestamp}"


@dataclass
class FlightPlan(Base):
    __tablename__ = 'flight_plans'
    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey('flights.id'))
    flight = relationship('Flights', back_populates='flight_plan')
    flight_rules = Column(String)
    aircraft = Column(String)
    aircraft_faa = Column(String)
    aircraft_short = Column(String)
    departure_airport = Column(String)
    arrival_airport = Column(String)
    alternate_airport = Column(String)
    cruise_tas = Column(Float)
    altitude = Column(String)
    deptime = Column(Integer)
    enroute_time = Column(Integer)
    fuel_time = Column(Integer)
    remarks = Column(String)
    route = Column(String)
    revision_id = Column(Integer)
    assigned_transponder = Column(Integer)

    def __init__(self, flight_rules, aircraft, aircraft_faa, aircraft_short, departure_airport, arrival_airport,
                 alternate_airport, cruise_tas, altitude, deptime, enroute_time, fuel_time, remarks, route, revision_id,
                 assigned_transponder):
        self.flight_rules = flight_rules
        self.aircraft = aircraft
        self.aircraft_faa = aircraft_faa
        self.aircraft_short = aircraft_short
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.alternate_airport = alternate_airport
        self.cruise_tas = cruise_tas
        self.altitude = altitude
        self.deptime = deptime
        self.enroute_time = enroute_time
        self.fuel_time = fuel_time
        self.remarks = remarks
        self.route = route
        self.revision_id = revision_id
        self.assigned_transponder = assigned_transponder

    @classmethod
    def from_dict(cls, data):
        return FlightPlan(**data)

    def to_dict(self):
        return asdict(self)


class FlightUpdate(Base):
    __tablename__ = 'flight_updates'
    id = Column(Integer, primary_key=True)
    cid = Column(Integer)
    callsign = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(String)
    groundspeed = Column(Float)
    heading = Column(Float)
    transponder = Column(Integer)
    flight_plan = Column(String)
    logon_time = Column(String)
    last_updated = Column(String)
    timestamp = Column(Integer)
    flight_id = Column(Integer, ForeignKey('flights.id'))
    flight = relationship('Flights', back_populates='flight_update')

    def __init__(self, cid, callsign, latitude, longitude, altitude, groundspeed, heading, transponder, flight_plan,
                 logon_time, last_updated, timestamp, flight):
        self.cid = cid
        self.callsign = callsign
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.groundspeed = groundspeed
        self.heading = heading
        self.transponder = transponder
        self.flight_plan = flight_plan
        self.logon_time = logon_time
        self.last_updated = last_updated
        self.timestamp = timestamp
        self.flight = flight


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
