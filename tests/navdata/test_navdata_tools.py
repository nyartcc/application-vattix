import sqlite3

import pytest

from navdata.tools import create_table, create_base_tables


@pytest.fixture
def session():  # Create a session for testing
    connection = sqlite3.connect(':memory:')
    db_session = connection.cursor()
    yield db_session
    connection.close()


def test_create_table(session):  # Verify that we can create a table
    create_table_sql = '''
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER
        );  '''

    assert create_table(session, create_table_sql) is True


def test_create_base_tables(session):  # Try to create the base tables
    assert create_base_tables(session) is True


def test_insert_general():  # Try to insert general information

    general = ["version", 1, "2203.3"]

    assert True  # FIXME - Implement this test
