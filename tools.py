import json
import os
import os.path
import sqlite3
from sqlite3 import Error


def connect_db(db_file):
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error as e:
        print(e)


def create_table(con, create_table_sql):
    """
    Create a table using the createTableSql statement
    :param con: The connection object
    :param create_table_sql: an SQL Statement to CREATE TABLE´
    :return:
    """
    try:
        c = con.cursor()
        c.execute(create_table_sql)
        return True
    except Error as e:
        print(e)
        return False


def create_base_tables(con):
    """

    :param con:
    :return:
    """
    # Queries for creating tables if they do not exist.
    sql_create_country_table = """ CREATE TABLE IF NOT EXISTS countries (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL,
                                            code text,
                                            type text
                                        );"""
    sql_create_airport_table = """ CREATE TABLE IF NOT EXISTS airports (
                                            id integer PRIMARY KEY,
                                            icao text NOT NULL,
                                            name text,
                                            latitude float,
                                            longitude float,
                                            iata text,
                                            fir text,
                                            test text,
                                            isPseudo bool default 0
                                        );"""
    sql_create_fir_table = """ CREATE TABLE IF NOT EXISTS firs (
                                        id integer PRIMARY KEY,
                                        icao text NOT NULL,
                                        name text,
                                        callsignprefix text,
                                        firboundary text
                                    );"""
    sql_create_uir_table = """ CREATE TABLE IF NOT EXISTS uirs (
                                        id integer PRIMARY KEY,
                                        prefix text,
                                        name text,
                                        coveragefirs text
                                    );"""
    sql_create_idl_table = """ CREATE TABLE IF NOT EXISTS idl (
                                                id integer PRIMARY KEY,
                                                cord1 text,
                                                cord2 text
                                            );"""
    sql_create_general_table = """ CREATE TABLE IF NOT EXISTS general (
                                                id integer PRIMARY KEY,
                                                version text,
                                                lastupdated int,
                                                vatspydata text
                                                );"""

    # If connection is successful, run the SQL to create the tables.
    try:
        create_table(con, sql_create_country_table)
        create_table(con, sql_create_airport_table)
        create_table(con, sql_create_fir_table)
        create_table(con, sql_create_uir_table)
        create_table(con, sql_create_idl_table)
        create_table(con, sql_create_general_table)
        print("Success")
        return True
    except Error as e:
        print("Something failed:", e)
        return False


def insert_general(con, general):
    """

    :param con:
    :param general:
    :return:
    """

    check = check_duplicate(con, 'general', 'id', 1)

    if check is not True:
        sql = ''' REPLACE INTO general('version', 'lastUpdated', 'vatspyData')
                    VALUES(?,?,?)'''
    else:
        sql = ''' UPDATE general SET version=?, lastupdated=?, vatspydata=? WHERE id=1'''

    cur = con.cursor()
    cur.execute(sql, general)
    con.commit()
    return True, cur.lastrowid


def insert_country(con, country):
    """
    Inserts a country in the database.
    :param con: The connection object.
    :param country: The object with the information about the country you wish to insert in the database.
    :return: True if successful along with the id of the row inserted.
    """

    check = check_duplicate(con, 'countries', 'code', country[1])

    if check is True:
        sql = '''UPDATE countries SET countries.name={0}, countries.code={1}, countries.type={2} WHERE id={3}'''.format(
            country[0], country[1], country[2], check[1])
        action = "Updated"
    else:
        sql = ''' REPLACE INTO countries('name', 'code', 'type')
                VALUES(?,?,?)'''
        action = "Inserted"

    try:
        cur = con.cursor()
        cur.execute(sql, country)
        con.commit()
        return True, cur.lastrowid, action
    except Error as e:
        print("WTF?", e)
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
                    VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')'''.format(
            airport.icao, airport.name, airport.latitude, airport.longitude, airport.iata, airport.fir,
            airport.is_pseudo)
        action = "insert"

    try:
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
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
    check = check_duplicate(con, "fir", "icao", fir.icao)

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
        sql = ''' REPLACE INTO firs (icao, name, callsignprefix, firboundary) VALUES (
        '{0}', '{1}', '{2}', '{3}')'''.format(
            fir.icao, fir.name, fir.callsign_prefix, fir.fir_boundary)
        action = "insert"

    try:
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        return True, cur.lastrowid, action
    except Error as e:
        print("Failed to {} fir {}:".format(action, fir.icao), e)
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
    cur = con.cursor()
    sql = "SELECT * FROM {} WHERE {} = '{}'".format(table, value1, value2)
    cur.execute(sql)
    row = cur.fetchone()

    if row is None:
        return False
    else:
        return True, row[0]
