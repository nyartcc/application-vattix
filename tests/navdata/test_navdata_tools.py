import sqlite3

import pytest

from navdata.classes import Country, General
from navdata.tools import create_table, create_base_tables, insert_country, insert_general


@pytest.fixture
def session():
    """
    Create a session for testing
    """
    connection = sqlite3.connect(':memory:')
    db_session = connection.cursor()
    yield db_session
    connection.close()


@pytest.fixture
def test_create_table(session):
    """
    Verify that we can create a table
    """
    cursor = session
    create_table_sql = '''
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER
        );  '''

    assert create_table(cursor, create_table_sql) is True
    yield cursor


@pytest.fixture
def test_create_base_tables(session, test_create_table):  # Try to create the base tables
    """
    Test creating the base tables
    """
    assert create_base_tables(session) is True
    yield session


def test_insert_general(session, test_create_base_tables):  # Try to insert general information

    general = ("version", 1, "2203.3")
    insert = insert_general(session, general)
    assert insert[0] is True



@pytest.mark.usefixtures("test_create_base_tables")
def test_insert_country(session, test_create_base_tables):
    """
    Test inserting a country into the database
    """
    cursor = session  # Get the cursor
    test_country = Country(name="Test Country", code="TC", type="Test Type")  # Create a test country
    insert = insert_country(cursor, test_country)  # Insert the country

    assert insert[0] is True  # Use the first return and verify that it is True
