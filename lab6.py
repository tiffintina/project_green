#!/usr/bin/python

import MySQLdb
import sys
import httplib
# Open database connection
db = MySQLdb.connect("127.0.0.1","root","4321","iotfarm")

# prepare a cursor object using cursor() method
cursor = db.cursor()
def get_status_code(url,path="/"):
	try:
		conn = httplib.HTTPConnection(url)
		conn.request("HEAD",path)
		return conn.getresponse().status
	except:
		return None
		
	
sql = """SELECT c.sensor_name,AVG(d.sensor_values) AS SENSOR_VALUES
FROM sensor c
LEFT JOIN (SELECT a.IP,b.sensor_values,b.last_update,b.sensor_id
FROM plant a 
LEFT JOIN sensor_transection b 
ON a.id = b.plant_id ) d on c.sensor_id = d.sensor_id 
WHERE d.IP = '192.168.0.1'and d.last_update between '2017-01-01 12:00:00' and  '2017-01-01 14:00:00'
group by sensor_name """
try:
	# Execute the SQL command
	cursor.execute(sql)
	# Fetch all the rows in a list of lists.
	results = cursor.fetchall()
	print "Status Code : {0}".format(get_status_code("localhost"))
	s = '{\n\t"code":200,\n\t"message":"SUCCESS",\n\t"results":[\n'
	for row in results:
		s += '\t\t{ "SENSOR_NAME" : '
		sensor_name = row[0]
		sensor_values = row[1]
		s+= '"{0}","VALUE" : {1}'.format(sensor_name,sensor_values)
		#s += sensor_name +", 'value:'"+ sensor_values
		s += "},\n"
	s += "\t]\n}"
	print s
except:
	#print "Error: unable to fecth data"
	print "Unexpected error:", sys.exc_info()[0]
	# disconnect from server
db.close()


