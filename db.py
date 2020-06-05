import sqlite3


def conn():
    return sqlite3.connect('base-db')
