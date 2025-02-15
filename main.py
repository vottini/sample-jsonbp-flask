
from flask import Flask
from flask import request
from flask import jsonify

import jsonbp

app = Flask(__name__)
blueprints = jsonbp.load_file('blueprints.jbp')
deserializer = blueprints.choose_root('Parameters')

@app.route("/plus", methods=["POST"])
def addition():
	encoding = request.content_encoding or 'utf-8'
	payload = request.data.decode(encoding)
	success, outcome = deserializer.deserialize(payload)

	if not success:
		result = jsonify(str(outcome))
		result.status_code = 400
		return result

	additionResponse = outcome['operand1'] + outcome['operand2']
	return str(additionResponse)

#------------------------------------------------------------

def get_request_payload():
	encoding = request.content_encoding or 'utf-8'
	return request.data.decode(encoding)

def make_error(msg):
	result = jsonify(str(msg))
	result.status_code = 400
	return result

def feed_json(function):
	def wrapped():
		payload = get_request_payload()
		success, outcome = deserializer.deserialize(payload)

		if not success:
			return make_error(outcome)

		return function(outcome)

	return wrapped


@app.route("/minus", methods=["POST"])
@feed_json
def subtraction(payload):
	response = payload['operand1'] - payload['operand2']
	return str(response)

#------------------------------------------------------------

import functools

def parse_json(root_type):
	blueprints = jsonbp.load_file("blueprints.jbp")
	deserializer = blueprints.choose_root(root_type)

	def deserialization_decorator(function):
		@functools.wraps(function)
		def wrapped(*args, **kargs):
			payload = get_request_payload()
			success, outcome = deserializer.deserialize(payload)

			if not success:
				return make_error(outcome)

			return function(outcome, *args, **kargs)

		return wrapped

	return deserialization_decorator


@app.route("/times", methods=["POST"])
@parse_json("Parameters")
def multiplication(payload):
	response = payload['operand1'] * payload['operand2']
	return str(response)

#------------------------------------------------------------

import umapper

def deserialize_json(root_type):
	blueprints = jsonbp.load_file("blueprints.jbp")
	deserializer = blueprints.choose_root(root_type)

	def deserialization_decorator(function):
		@functools.wraps(function)
		def wrapped(*args, **kargs):
			payload = get_request_payload()
			success, outcome = deserializer.deserialize(payload)

			if not success:
				return make_error(outcome)

			return function(
				umapper.convert_to_object(outcome),
				*args, **kargs)

		return wrapped

	return deserialization_decorator

@app.route("/divide", methods=["POST"])
@deserialize_json("Parameters")
def division(payload):
	response = payload.operand1 / payload.operand2
	return str(response)

#------------------------------------------------------------

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)

