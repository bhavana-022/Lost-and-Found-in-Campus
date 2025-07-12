# db.py

import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root123",
        database="lost_and_found_db"  # use `database=` not `db=`
    )
