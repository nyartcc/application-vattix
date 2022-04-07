from navdata.classes import Airport, Country
from tools import db_init


def test_field_access():
    a = Airport("ENZV", "Stavanger", 54.1, -12, {"latitude": 54.1, "longitude": -12}, "SVG", "ENSV", 0, 123)
    assert a.icao == "ENZV"
    assert a.name == "Stavanger"
    assert a.latitude == 54.1
    assert a.longitude == -12
    assert a.position == {"latitude": 54.1, "longitude": -12}
    assert a.iata == "SVG"
    assert a.fir == "ENSV"
    assert a.is_pseudo == 0
    assert a.id == 123


def test_defaults():
    a = Airport()
    assert a.icao is None
    assert a.name is None
    assert a.latitude is None
    assert a.longitude is None
    assert a.iata is None
    assert a.fir is None
    assert a.is_pseudo == 0
    assert a.id is None


def test_equality():
    a1 = Airport("ENZV", "Stavanger", 54.1, -12, {"latitude": 54.1, "longitude": -12}, "SVG", "ENSV", 0, 123)
    a2 = Airport("ENZV", "Stavanger", 54.1, -12, {"latitude": 54.1, "longitude": -12}, "SVG", "ENSV", 0, 123)
    assert a1 == a2


def test_quality_with_diff_ids():
    a1 = Airport("ENZV", "Stavanger", 54.1, -12, {"latitude": 54.1, "longitude": -12}, "SVG", "ENSV", 0, 123)
    a2 = Airport("ENZV", "Stavanger", 54.1, -12, {"latitude": 54.1, "longitude": -12}, "SVG", "ENSV", 0, 4567)
    assert a1 == a2


def test_inequality():
    a1 = Airport("ENZV", "Stavanger", 54.1, -12, {"latitude": 54.1, "longitude": -12}, "SVG", "ENSV", 0, 123)
    a2 = Airport("KJFK", "Kennedy Intl.", 40.3, 73.4, {"latitude": 40.3, "longitude": 73.4}, "JFK", "KZNY", 0, 123)
    assert a1 != a2


def test_from_dict():
    a1 = Airport("ENZV", "Stavanger", 54.1, -12, {"latitude": 54.1, "longitude": -12}, "SVG", "ENSV", 0, 123)
    a2_dict = {
        "icao": "ENZV",
        "name": "Stavanger",
        "latitude": 54.1,
        "longitude": -12,
        "position": {"latitude": 54.1, "longitude": -12},
        "iata": "SVG",
        "fir": "ENSV",
        "is_pseudo": 0,
        "id": 123,
    }
    a2 = Airport.from_dict(a2_dict)
    assert a1 == a2

def test_to_dict():
    a1 = Airport("ENZV", "Stavanger", 54.1, -12, {"latitude": 54.1, "longitude": -12}, "SVG", "ENSV", 0, 123)
    a2 = a1.to_dict()
    a2_expected = {
        "icao": "ENZV",
        "name": "Stavanger",
        "latitude": 54.1,
        "longitude": -12,
        "position": {"latitude": 54.1, "longitude": -12},
        "iata": "SVG",
        "fir": "ENSV",
        "is_pseudo": 0,
        "id": 123
    }
    assert a2 == a2_expected

def test_airport_info():
    a1 = Airport("ENZV", "Stavanger", 54.1, -12, {"latitude": 54.1, "longitude": -12}, "SVG", "ENSV", 0, 123)

    con = db_init.connect_db("dev.db")

    assert(Airport.info(con, "ENZV", "coordinates") == {'lat': -9.191365, 'lon': 160.948836})
    assert(Airport.info(con, "ENZV", "country") is None)
