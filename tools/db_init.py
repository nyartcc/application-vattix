import logging
import os
import sqlite3

from sqlite3 import Error


def sql_table(con):

    try:
        con.execute(
            "CREATE TABLE connections (id integer PRIMARY KEY, cid integer, callsign text, latitude float, "
            "longitude float, altitude float, groundspeed float, transponder text, heading float, flight_plan text, "
            "logon_time text, last_updated text)")

        con.execute(
            "CREATE TABLE flight_updates (id integer PRIMARY KEY, connection_id int, update_id int, cid int, latitude float, "
            "longitude float, altitude float, groundspeed float, transponder int, heading int, flight_plan text, "
            "departure_time text, arrival_time int, update_time int, departed int, arrived int)")

        return True
    except Error as e:  # pragma: no cover
        return False, e


def connect_db(db_file):
    con = None
    con = sqlite3.connect(db_file)
    return con