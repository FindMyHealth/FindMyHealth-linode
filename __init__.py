from flask import Flask, abort, request, jsonify
import requests
import mysql.connector
from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from secret import db_password, google_secret_key

app = Flask(__name__)

google_key = google_secret_key

# database setup
my_host = "localhost"
my_username = "root"
my_password = db_password
my_database = "health"

# establish MySQL connection
cnx = mysql.connector.connect(user=my_username, password=my_password,host=my_host,database=my_database)
cursor = cnx.cursor()

@app.route("/")
def hello():
	return "Hello, I love Linode!"

@app.route("/api/v0.1/hospitals", methods=['GET'])
def hospitals():
	# if the parameter isn't set...
	if not 'coordinates' in request.args:
		abort(400)
	else:
		# Method to determine if a string is a floating point value or not
		def isFloat(string):
			try:
				float(string)
				return True
			except ValueError:
				return False
		
		try:
			words = (request.args['coordinates']).split(',')
		except:
			words = [1]
		
		if len(words) == 2 and isFloat(words[0]) and isFloat(words[1]):
			# initial request
			base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
			payload = {
				'key': google_key,
				'rankby': 'prominence',
				'radius':'50000',
				'location':request.args['coordinates'],
				'types':'hospital'
			}

			response = requests.get(base_url, params=payload)
			json = response.json()
			hospitals = json['results']
			valid_hospitals = []

			for hospital in hospitals:
				cursor.execute("SELECT * FROM states_averages WHERE g_place_id = (%s)", (hospital['place_id'],)) 
				hlist = cursor.fetchall()
				if len(hlist) > 0:
					hlist.append(hospital['name'])
					driving_url = "https://maps.googleapis.com/maps/api/directions/json"
					payload = {
						'key':google_key,
						'origin':words[0] + "," + words[1],
						'destination':str(hospital['geometry']['location']['lat']) + "," + str(hospital['geometry']['location']['lng']) 
					}
					minutes = requests.get(driving_url, params=payload).json()
					if minutes['status'] == "OK":
						hlist.append(minutes['routes'][0]['legs'][0]['duration']['value'])
						valid_hospitals.append(hlist)

			if len(valid_hospitals) > 0:
				data = []
				for hosp in valid_hospitals:
					arr = {
						'name' : hosp[1],
						'lat' : float(hosp[0][11]),
						'lng' : float(hosp[0][12]),
						'wait_time' : int(hosp[0][2]),
						'drive_time' : int(hosp[2]/60),
						'total_time' : int(hosp[0][2]) + int(hosp[2]/60),
						'address' : hosp[0][10],
						'phone' : hosp[0][8],
						'time_until_sent_home' : int(hosp[0][3]),
						'broken_bone' : int(hosp[0][4]),
						'transfer_time' : int(hosp[0][5])
					}
					data.append(arr)
				
				data = jsonify({'data':data})
	
				return data

			else:
				return make_response(jsonify({'error':'Options not found!'}), 404)	
	
		else:
			abort(400)	


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
