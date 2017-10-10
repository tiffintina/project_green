#!/usr/bin/python

import MySQLdb

# Open database connection
db = MySQLdb.connect("127.0.0.1","root","4321","iotfarm" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# Prepare SQL query to INSERT a record into the database.
sql = """INSERT INTO sensor
VALUES (1,'DHT',now())"""
try:
   # Execute the SQL command
   cursor.execute(sql)
   # Commit your changes in the database
   db.commit()
except:
   # Rollback in case there is any error
   db.rollback()

# disconnect from server
db.close()