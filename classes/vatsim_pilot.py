from dataclasses import dataclass, field, asdict


@dataclass
class Pilot:
    cid: int
    name: str
    callsign: str
    server: str
    pilot_rating: int
    latitude: float
    longitude: float
    altitude: int
    groundspeed: int
    transponder: int
    heading: int
    qnh_i_hg: float
    qnh_mb: float
    flight_plan: dict
    logon_time: str
    last_updated: str
    id: int = field(default=None, compare=False)

    @classmethod
    def from_dict(cls, d):
        return Pilot(**d)

    def to_dict(self):
        return asdict(self)

@dataclass()
class Flightplan:
    flight_rules: str
    aircraft: str
    aircraft_faa: str
    aircraft_short: str
    departure: str
    arrival: str
    alternate: str
    cruise_tas: str
    altitude: str
    deptime: str
    enroute_time: str
    fuel_time: str
    remarks: str
    route: str
    revision_id: int
    assigned_transponder: str

    @classmethod
    def from_dict(cls, d):
        return Flightplan(**d)

