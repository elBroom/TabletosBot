import sqlite3
import config

con = sqlite3.connect(config.DB_PATH.replace('sqlite:///', ''))
cur = con.cursor()

sql_file = open("init.sql")
sql_as_string = sql_file.read()
cur.executescript(sql_as_string)
