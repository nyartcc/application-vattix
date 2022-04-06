import sqlite3

import pytest

from tools import db_init


@pytest.fixture
def session():
    connection = sqlite3.connect(':memory:')
    db_session = connection.cursor()
    yield db_session
    connection.close()


@pytest.fixture
def setup_database(session):
    session.execute('CREATE TABLE flight_updates (id integer PRIMARY KEY, connection_id int, update_id int, cid int,'
                    'latitude float, longitude float, altitude float, groundspeed float, transponder int, heading int,'
                    'flight_plan text, departure_time text, arrival_time int, update_time int, departed int,'
                    'arrived int)')
    yield session


@pytest.fixture
def setup_test_data1(setup_database):
    cursor = setup_database

    sample_data = [
        (1, 2, 3, 4, 5, 6, 7, 8, 9, "flight_plan", "departure_time", "arrival_time", 10, 11, 12, 25),
        (13, 14, 15, 16, 17, 18, 19, 20, 21, "flight_plan", "departure_time", "arrival_time", 22, 23, 24, 26),
    ]

    cursor.executemany("INSERT INTO flight_updates VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", sample_data)
    yield cursor


def test_with_sample_data1(setup_test_data1):
    cursor = setup_test_data1
    cursor.execute("SELECT * FROM flight_updates")
    assert len(list(cursor.execute("SELECT * FROM flight_updates"))) == 2


def test_sql_connection():  # Test that the dev database is created
    assert db_init.connect_db("dev.db") is not False


def test_sql_table(session):  # Test we are able to create the correct tables in the database
    assert db_init.sql_table(session) is True




