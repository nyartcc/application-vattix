import logging
import os
import sqlite3
from sqlite3 import Error
from tools import helper

config = helper.read_config()
country_table = config['DatabaseSettings']['countries_table']
airport_table = config['DatabaseSettings']['airports_table']
general_table = config['DatabaseSettings']['general_table']
fir_table = config['DatabaseSettings']['firs_table']
uir_table = config['DatabaseSettings']['uirs_table']
idl_table = config['DatabaseSettings']['idl_table']


def connect_db(db_file):
    con = None

    con = sqlite3.connect(db_file)
    con = con.cursor()
    return con


def create_table(con, create_table_sql):
    """
    Create a table using the createTableSql statement
    :param con: The connection object
    :param create_table_sql: an SQL Statement to CREATE TABLE´
    :return:
    """
    try:
        c = con
        c.execute(create_table_sql)
        return True
    except Error as e:
        logging.exception(e)
        return False


def create_base_tables(con):
    """
    Creates the initial base tables for the database. Get the table names from the config file.
    :param con: The connection object.
    :return: True / False. If false, also return the error message.
    """
    # Queries for creating tables if they do not exist.
    sql_create_country_table = ''' CREATE TABLE IF NOT EXISTS {0} (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL,
                                            code text,
                                            type text
                                        );'''.format(country_table)
    sql_create_airport_table = """ CREATE TABLE IF NOT EXISTS {0} (
                                            id integer PRIMARY KEY,
                                            icao text NOT NULL,
                                            name text,
                                            latitude float,
                                            longitude float,
                                            iata text,
                                            fir text,
                                            test text,
                                            isPseudo bool default 0
                                        );""".format(airport_table)
    sql_create_fir_table = """ CREATE TABLE IF NOT EXISTS {0} (
                                        id integer PRIMARY KEY,
                                        icao text NOT NULL,
                                        name text,
                                        callsignprefix text,
                                        firboundary text
                                    );""".format(fir_table)
    sql_create_uir_table = """ CREATE TABLE IF NOT EXISTS {0} (
                                        id integer PRIMARY KEY,
                                        prefix text,
                                        name text,
                                        coveragefirs text
                                    );""".format(uir_table)
    sql_create_idl_table = """ CREATE TABLE IF NOT EXISTS {0} (
                                                id integer PRIMARY KEY,
                                                cord1 text,
                                                cord2 text
                                            );""".format(idl_table)
    sql_create_general_table = """ CREATE TABLE IF NOT EXISTS {0} (
                                                id integer PRIMARY KEY,
                                                version text,
                                                lastupdated int,
                                                vatspydata text
                                                );""".format(general_table)

    # If connection is successful, run the SQL to create the tables.
    create_table(con, sql_create_country_table)
    create_table(con, sql_create_airport_table)
    create_table(con, sql_create_fir_table)
    create_table(con, sql_create_uir_table)
    create_table(con, sql_create_idl_table)
    create_table(con, sql_create_general_table)
    return True


def insert_general(con, general, **kwargs):
    """
    Insert or update the general settings in the database.
    :param con: The connection object.
    :param general: The object with the information about the general information that one wish to insert in
                    the database.
    :return: True - If the query is successful, along with the row id of the inserted row.
    """

    check = check_duplicate(con, general_table, 'id', 1)

    if check[0] is not True:
        sql = ''' INSERT INTO {}('version', 'lastUpdated', 'vatspyData')
                    VALUES(?,?,?)'''.format(general_table)
    else:
        sql = ''' UPDATE {} SET version=?, lastupdated=?, vatspydata=? WHERE id=1'''.format(general_table)

    try:
        if kwargs.get('column'):
            con.execute(sql, kwargs.get('column'))
        else:
            con.execute(sql, general)
        return True
    except Error as e:
        logging.exception(e)
        return False


def insert_country(con, country):
    """
    Inserts a country in the database.
    :param con: The connection object.
    :param country: The object with the information about the country you wish to insert in the database.
    :return: True if successful along with the id of the row inserted.
    """

    check = check_duplicate(con, country_table, 'id', country.id)

    if check is True:
        sql = '''UPDATE countries SET countries.name={0}, countries.code={1}, countries.type={2} WHERE id={3}'''.format(
            country.name, country.code, country.type, check[1])
        action = "Updated"
    else:
        sql = ''' REPLACE INTO countries('name', 'code', 'type')
                    VALUES("{}","{}","{}")'''.format(country.name, country.code, country.type)
        action = "Inserted"

    try:
        con.execute(sql)
        # con.commit()
        return True, con.lastrowid, action
    except Error as e:
        print("Failed to insert country {}. Error:".format(country.name), e)
        return False


def insert_airport(con, airport):
    """

    :param con:
    :param airport:
    :return:
    """
    check = check_duplicate(con, 'airports', 'icao', airport.icao)

    if check is True:
        sql = '''UPDATE airports SET (
                    airports.icao={0}, 
                    airports.name={1}, 
                    airports.latitude={2}, 
                    airports.longitude={3},
                    airports.iata={4},
                    airports.fir={5},
                    airports.isPseudo={6}
                    ) WHERE id={7}'''.format(
            airport.icao, airport.name, airport.latitude, airport.longitude, airport.iata, airport.fir,
            airport.is_pseudo, check[1])
        action = "update"
    else:
        sql = ''' REPLACE INTO airports (icao, name, latitude, longitude, iata, fir, isPseudo) 
                    VALUES ("{0}","{1}","{2}","{3}","{4}","{5}","{6}")'''.format(
            airport.icao, airport.name, airport.latitude, airport.longitude, airport.iata, airport.fir,
            airport.is_pseudo)
        action = "insert"

    try:
        cur = con
        con.execute(sql)
        #con.commit()
        return True, cur.lastrowid, action
    except Error as e:
        print("Failed to {} airport {} :".format(action, airport.icao), e)
        return False


def insert_fir(con, fir):
    """
    Insert or update an FIR in the database.
    :param con: The SQL connection
    :param fir: The FIR object, consisting of an ICAO, Name, Callsign Prefix and FIR Boundary
    :return: If successful - True, the ID of the last inserted row as well as what action [insert/update] was performed
             If failed - False
    """
    check = check_duplicate(con, "firs", "icao", fir.icao)

    if check is True:
        sql = '''UPDATE firs SET (
                firs.icao={0},
                firs.name={1},
                firs.callsignprefix={2},
                firs.firboundary={3}
                ) WHERE id={4}'''.format(
            fir.icao, fir.name, fir.callsign_prefix, fir.fir_boundary, check[1])
        action = "update"
    else:
        sql = ''' REPLACE INTO firs (icao, name, callsignprefix, firboundary) 
        VALUES ('{0}','{1}','{2}','{3}')'''.format(
            fir.icao, fir.name, fir.callsign_prefix, fir.fir_boundary)
        action = "insert"

    try:
        cur = con
        cur.execute(sql)
        # con.commit()
        return True, cur.lastrowid, action
    except Error as e:
        print("Failed to {} thing {}:".format(action, fir.icao), e)
        return False


def insert_uir(con, uir):
    """

    :param con:
    :param uir:
    :return:
    """
    check = check_duplicate(con, uir_table, "name", uir.name)

    if check is True:
        sql = '''UPDATE {0} SET (
                {0}.prefix={1}
                {0}.prefix={2}
                {0}.prefix={3}
        ) WHERE id={4}'''.format(
            uir_table, uir.prefix, uir.name, uir.coverage_firs, check[1])
        action = "update"
    else:
        sql = ''' REPLACE INTO {0} (prefix, name, coveragefirs)
                VALUES('{1}', '{2}', '{3}')'''.format(
            uir_table, uir.prefix, uir.name, uir.coverage_firs)
        action = "insert"

    try:
        cur = con
        cur.execute(sql)
        # con.commit()
        return True, cur.lastrowid, action
    except Error as e:
        print("Failed to {} UIR {}:".format(action, uir.name), e)
        return False


def delete_idl(con):
    drop_previous_idl = ''' DELETE FROM {} WHERE id > 0'''.format(idl_table)
    try:
        cur = con
        cur.execute(drop_previous_idl)
        # con.commit()

        return True
    except Error as e:
        print("Failed to delete IDL", e)
        return False


def insert_idl(con, idl):
    """
    Insert the International Date Line (IDL) in the database. Make sure to run delete_idl() first!
    :param con: The connection object.
    :param idl: The IDL object containing the two coordinates.
    :return: True / Fail. If true, return the last inserted row id, along with the action.
    """
    sql = ''' INSERT INTO {0} (cord1, cord2) VALUES ({1}, {2})'''.format(idl_table, idl.cord1, idl.cord2)
    action = "insert"

    try:
        cur = con
        cur.execute(sql)
        # con.commit()

        return True, cur.lastrowid, action
    except Error as e:
        print("Failed to modify IDL...", e)
        return False


def check_duplicate(con, table, value1, value2):
    """
    Checks if a row already exists in the table specified
    :param con: The connection object
    :param table: The table you wish to query
    :param value1: The comparison column
    :param value2: The comparison object
    :return: True if there is a duplicate along with the duplicate row id.
    """
    sql = "SELECT * FROM {} WHERE {} = '{}'".format(table, value1, value2)
    con.execute(sql)
    row = con.fetchone()

    if row is None:
        return False, None
    else:
        return True, row[0]
