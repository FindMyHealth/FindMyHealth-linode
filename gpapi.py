# imports
from lxml import html
import requests
import mysql.connector
import time
import json

# database credentials
my_host = "localhost"
my_username = "root"
my_password = ""
my_database = "health"

# establish MySQL connection
cnx = mysql.connector.connect(user=my_username, password=my_password,host=my_host,database=my_database)
cursor = cnx.cursor()

GOOGLE_SECRET_KEY = "AIzaSyBh5wArbL1a6TrV_39GWwUaTF8JtkIWLoM"

cursor.execute("SELECT id, hospital_name, address FROM states_averages")
data = cursor.fetchall()

for point in data:
	payload = {
		"key" : GOOGLE_SECRET_KEY,
		"query" : point[2] + ", " + point[3]
	}

	response = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params=payload).json()

	if response['status'] == "OK": 
		try:
			cursor.execute("UPDATE states_averages SET g_address = %s, g_lat = %s, g_lng = %s, g_place_id = %s WHERE id = %s", (response['results'][0]['formatted_address'], response['results'][0]['geometry']['location']['lat'], response['results'][0]['geometry']['location']['lng'], response['results'][0]['place_id'], point[0]))
			cnx.commit()
			print response
		except:
			print "Skipped something!"
	else:
		print "ERROR - ERROR - ERROR"
