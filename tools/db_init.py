import sqlite3

from sqlite3 import Error


def sql_connection():
    try:
        db_file = '../dev.db'
        con = sqlite3.connect(db_file)

        return con, db_file

    except Error:
        print(Error)


def sql_table(con):
    cursorObj = con.cursor()

    try:
        cursorObj.execute(
        "CREATE TABLE connections (id integer PRIMARY KEY, cid integer, callsign text, latitude float, "
        "longitude float, altitude float, groundspeed float, transponder text, heading float, flight_plan text, "
        "logon_time text, last_updated text)")

        cursorObj.execute(
            "CREATE TABLE flights (id integer PRIMARY KEY, connection_id int, update_id int, cid int, latitude float, "
            "longitude float, altitude float, groundspeed float, transponder int, heading int, flight_plan text, "
            "departure_time text, arrival_time int, update_time int, departed int, arrived int)")

        con.commit()
        return True
    except Error as e:
        return False, e


def connect_db(db_file):
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error as e:
        print(e)

