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

	elif action == 'get_leave':
		response = get_leave()

	elif action == 'create_event':
		response = create_event(req)

	elif action == 'delete_event':
		response = delete_event(req)

	elif action == 'get_reschedule_event':
		response = get_reschedule_event(req)

	elif action == 'reschedule_event':
		response = reschedule_event(req)

	return { "fulfillmentMessages" : response }
		
if __name__ == '__main__':
  app.run()
