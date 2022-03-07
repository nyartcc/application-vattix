import json
import os
import os.path
import sqlite3
from sqlite3 import Error


def connectDb(db_file):
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error as e:
        print(e)


def createTable(con, createTableSql):
    """
    Create a table using the createTableSql statement
    :param con: The connection object
    :param createTableSql: an SQL Statement to CREATE TABLE´
    :return:
    """
    try:
        c = con.cursor()
        c.execute(createTableSql)
        return True
    except Error as e:
        print(e)
        return False


def createBaseTables(con):
    """

    :param con:
    :return:
    """
    # Queries for creating tables if they do not exist.
    sqlCreateCountryTable = """ CREATE TABLE IF NOT EXISTS countries (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL,
                                            code text,
                                            type text
                                        );"""
    sqlCreateAirportTable = """ CREATE TABLE IF NOT EXISTS airports (
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
    sqlCreateFirTable = """ CREATE TABLE IF NOT EXISTS firs (
                                        id integer PRIMARY KEY,
                                        icao text NOT NULL,
                                        name text,
                                        callsignprefix text,
                                        firboundary text
                                    );"""
    sqlCreateUirTable = """ CREATE TABLE IF NOT EXISTS uirs (
                                        id integer PRIMARY KEY,
                                        prefix text,
                                        name text,
                                        coveragefirs text
                                    );"""
    sqlCreateIdlTable = """ CREATE TABLE IF NOT EXISTS idl (
                                                id integer PRIMARY KEY,
                                                cord1 text,
                                                cord2 text
                                            );"""
    sqlCreateGeneralTable = """ CREATE TABLE IF NOT EXISTS general (
                                                id integer PRIMARY KEY,
                                                version text,
                                                lastupdated int,
                                                vatspydata text
                                                );"""

    # If connection is successful, run the SQL to create the tables.
    try:
        createTable(con, sqlCreateCountryTable)
        createTable(con, sqlCreateAirportTable)
        createTable(con, sqlCreateFirTable)
        createTable(con, sqlCreateUirTable)
        createTable(con, sqlCreateIdlTable)
        createTable(con, sqlCreateGeneralTable)
        print("Success")
        return True
    except Error as e:
        print("Something failed:", e)
        return False


def insertGeneral(con, general):
    """

    :param con:
    :param general:
    :return:
    """

    check = checkDuplicate(con, 'general', 'id', 1)

    if check is not True:
        sql = ''' REPLACE INTO general('version', 'lastUpdated', 'vatspyData')
                    VALUES(?,?,?)'''
    else:
        sql = ''' UPDATE general SET version=?, lastupdated=?, vatspydata=? WHERE id=1'''

    cur = con.cursor()
    cur.execute(sql, general)
    con.commit()
    return True, cur.lastrowid


def insertCountry(con, country):
    """
    Inserts a country in the database.
    :param con: The connection object.
    :param country: The object with the information about the country you wish to insert in the database.
    :return: True if successful along with the id of the row inserted.
    """

    check = checkDuplicate(con, 'countries', 'code', country[1])

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


def insertAirport(con, airport):
    """

    :param con:
    :param airport:
    :return:
    """
    check = checkDuplicate(con, 'airports', 'icao', airport[0])

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
            airport[0], airport[1], airport[2], airport[3], airport[4], airport[5], airport[6], check[1])
        action = "update"
    else:
        sql = ''' REPLACE INTO airports (icao, name, latitude, longitude, iata, fir, isPseudo) VALUES (?,?,?,?,?,?,?)'''
        action = "insert"

    try:
        cur = con.cursor()
        cur.execute(sql, airport)
        con.commit()
        return True, cur.lastrowid, action
    except Error as e:
        print("Failed to {} airport {} :".format(action, airport[0]), e)
        return False


def checkDuplicate(con, table, value1, value2):
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



