#!/usr/bin/python

import MySQLdb

# Open database connection
db = MySQLdb.connect("127.0.0.1","root","4321","iotfarm" )

# prepare a cursor object using cursor() method
cursor = db.cursor()


sql = """INSERT INTO SENSOR_TRANSECTION 
VALUES (1,3,69.7,NOW())
"""

cursor.execute(sql)

# disconnect from server
db.close()