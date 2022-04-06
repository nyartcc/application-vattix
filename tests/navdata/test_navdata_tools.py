import sqlite3
from sqlite3 import Error

import pytest

from navdata.classes import Country, General, Airport, Fir, Uir, Idl
from navdata.tools import create_table, create_base_tables, insert_country, insert_general, insert_airport, insert_fir, \
    insert_uir, delete_idl, insert_idl, check_duplicate, connect_db


@pytest.fixture
def session():
    """
    Create a session for testing
    """
    connection = sqlite3.connect(':memory:')
    db_session = connection.cursor()
    yield db_session
    connection.close()


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

    # Create a test table and verify that it is created
    workingsql = create_table(cursor, create_table_sql)
    assert workingsql is True

    # Try to create a table with non valid SQL. Should return false.
    nonworkingsql = create_table(cursor, "Not a valid SQL statement")
    assert nonworkingsql is False


@pytest.fixture
def test_create_base_tables(session):  # Try to create the base tables
    """
    Test creating the base tables
    """
    create_tables = create_base_tables(session)
    assert create_tables is True  # Verify that the tables were created

    yield session


def test_connect_db():
    con = connect_db("dev.db")
    assert con is not None


def test_insert_general(session, test_create_base_tables):  # Try to insert general information

    general = ("version", 1, "2203.3")  # Create a general object
    insert = insert_general(session, general)  # Insert the general object - this should return True

    assert insert is True


def test_insert_duplicate_general(session, test_create_base_tables):
    general = ("version", 1, "2203.3")  # Create a general object
    insert_first = insert_general(session, general)  # Insert the first general object
    insert_second = insert_general(session, general)  # Insert the general object again - it should still return True
    assert insert_second is True


def test_insert_malformed_general(session, test_create_base_tables):
    """
    Test inserting a malformed general object
    """
    general = (None, None, None)  # This is a malformed general object, but irrelevant in this case.

    # Insert the general object - this should return False. However, in order to break the SQL statement, we need to
    # specify an incorrect column name, using the column value.
    non_working_insert = insert_general(session, general, column='malformed')
    assert non_working_insert is False


@pytest.mark.usefixtures("test_create_base_tables")
def test_insert_country(session, test_create_base_tables):
    """
    Test inserting a country into the database
    """
    cursor = session  # Get the cursor
    test_country = Country(name="Test Country", code="TC", type="Test Type")  # Create a test country
    insert = insert_country(cursor, test_country)  # Insert the country

    assert insert[0] is True  # Use the first return and verify that it is True


@pytest.mark.usefixtures("test_create_base_tables")
def test_insert_airport(session, test_create_base_tables):
    """
    Test inserting an airport into the database
    """
    cursor = session  # Get the cursor
    test_airport = Airport(icao="ABCD", name="Test Airport", latitude="54.9", longitude="-10.10",
                           iata="EFG", fir="HIJ", is_pseudo=0)  # Create a test airport
    insert = insert_airport(cursor, test_airport)  # Insert the airport

    assert insert[0] is True  # Use the first return and verify that it is True


@pytest.mark.usefixtures("test_create_base_tables")
def test_insert_duplicate_airport(session, test_create_base_tables):
    """
    Test inserting a duplicate airport into the database
    """
    cursor = session  # Get the cursor
    test_airport = Airport(icao="ABCD", name="Test Airport", latitude="549", longitude="1010",
                           iata="EFG", fir="HIJ", is_pseudo=0)  # Create a test airport

    insert_first = insert_airport(cursor, test_airport)  # Insert the first airport

    insert_second = insert_airport(cursor, test_airport)  # Insert the second airport - it should still return True
    assert insert_second[0] is True


@pytest.mark.usefixtures("test_create_base_tables")
def test_insert_malformed_airport(session, test_create_base_tables):
    """
    Test inserting a malformed airport into the database
    """
    cursor = session  # Get the cursor
    test_airport = Airport(icao="ABCD", name="Test Airport", latitude=54.9, longitude="ten",
                           iata="EFG", fir="HIJ", is_pseudo="yes")  # Create a test airport

    non_working_insert = insert_airport(cursor, test_airport)
    print(non_working_insert)
    #assert non_working_insert[0] is False



@pytest.mark.usefixtures("test_create_base_tables")
def test_insert_fir(session, test_create_base_tables):
    """
    Test inserting a FIR into the database
    """
    cursor = session  # Get the cursor
    test_fir = Fir(icao="ABCD", name="Test FIR", callsign_prefix="EFG", fir_boundary="HIJ")  # Create a test FIR
    insert = insert_fir(cursor, test_fir)  # Insert the FIR

    assert insert[0] is True  # Use the first return and verify that it is True


@pytest.mark.usefixtures("test_create_base_tables")
def test_insert_uir(session, test_create_base_tables):
    """
    Test inserting a UIR into the database
    """
    cursor = session  # Get the cursor
    test_uir = Uir(prefix="ABC", name="Test UIR", coverage_firs="DEF")  # Create a test UIR
    insert = insert_uir(cursor, test_uir)  # Insert the UIR

    assert insert[0] is True  # Use the first return and verify that it is True


@pytest.mark.usefixtures("test_create_base_tables")
def test_delete_idl(session, test_create_base_tables):
    """
    Test deleting all the existing IDL entries in the database
    """
    cursor = session  # Get the cursor

    delete = delete_idl(session)  # Execute the delete sql
    assert delete is True  # Verify that the row was deleted


@pytest.mark.usefixtures("test_create_base_tables")
def test_insert_idl(session, test_create_base_tables):
    """
    Test inserting an IDL into the database
    """
    cursor = session  # Get the cursor
    test_idl = Idl(cord1="123.45", cord2="234.56")  # Create a test IDL
    insert = insert_idl(cursor, test_idl)  # Insert the IDL

    assert insert[0] is True  # Use the first return and verify that it is True


@pytest.mark.usefixtures("test_create_base_tables")
def test_check_duplicate(session, test_create_base_tables):
    """
    Test checking for duplicate entries
    """
    cursor = session  # Get the cursor
    test_country = Country(name="Test Country", code="TC", type="Test Type")  # Create a test country
    insert_country(cursor, test_country)  # Insert the country

    assert check_duplicate(cursor, "countries", "code", "TC")[0] is True  # Verify that there is a duplicate
    assert check_duplicate(cursor, "countries", "code", "TEST")[0] is False  # Verify that there is no duplicate
