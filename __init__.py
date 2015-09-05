from flask import Flask, abort, request, jsonify
import requests
import mysql.connector
app = Flask(__name__)

google_key = 'AIzaSyBh5wArbL1a6TrV_39GWwUaTF8JtkIWLoM'

# database setup
my_host = "localhost"
my_username = "root"
my_password = "tPWrd5"
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
				'rankby': 'distance',
				'location':request.args['coordinates'],
				'types':'hospital'
			}

			response = requests.get(base_url, params=payload)
			json = response.json()
			hospitals = json['results']

			for hospital in hospitals:
				cursor.execute("SELECT hospital_name FROM states_averages WHERE g_place_id = \"" + hospital['place_id'] + "\"")				
				hospital = cursor.fetchall()
				print hospital	

			return "Test!" 
	
		else:
			print "fail!"
			abort(400)		


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
