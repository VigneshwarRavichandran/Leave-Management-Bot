from flask import Flask, jsonify, make_response, request
from response import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	return make_response(jsonify(results()))

def results():
	req = request.get_json(force=True)
	action = req['queryResult']['action']
	response = None
	username = 'Vigneshwar'
	leave_limit = 20

	if action == 'get_date':
		response = get_date(req, username, leave_limit)

	return { "fulfillmentMessages" : response }
		
if __name__ == '__main__':
  app.run()
