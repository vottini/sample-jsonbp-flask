
from flask import Flask
from flask import request
from flask import jsonify
import jsonbp

app = Flask(__name__)
operandsBlueprint = jsonbp.load('jsonBlueprints/twoNumbers.jbp')

@app.route("/plus", methods=["POST"])
def addition():
	encoding = request.content_encoding or 'utf-8'
	payload = request.data.decode(encoding)
	success, outcome = operandsBlueprint.deserialize(payload)

	if not success:
		result = jsonify(str(msg))
		result.status_code = 400
		return result

	additionResponse = outcome['operand1'] + outcome['operand2']
	return str(additionResponse)

#------------------------------------------------------------

def getRequestPayload():
	encoding = request.content_encoding or 'utf-8'
	return request.data.decode(encoding)

def makeError(msg):
	result = jsonify(str(msg))
	result.status_code = 400
	return result

def feedJSON(function):
	def wrap():
		payload = getRequestPayload()
		success, outcome = operandsBlueprint.deserialize(payload)
		if not success: return makeError(outcome)
		return function(outcome)

	return wrap


@app.route("/minus", methods=["POST"])
@feedJSON
def subtraction(payload):
	response = payload['operand1'] - payload['operand2']
	return str(response)

#------------------------------------------------------------

import functools

def deserializeJSON(blueprintFile):
	blueprint = jsonbp.load(blueprintFile)

	def deserializationDecorator(function):
		@functools.wraps(function)
		def wrap(*args, **kargs):
			payload = getRequestPayload()
			success, outcome = blueprint.deserialize(payload)
			if not success: return makeError(outcome)
			return function(outcome, *args, **kargs)

		return wrap

	return deserializationDecorator


@app.route("/times", methods=["POST"])
@deserializeJSON("jsonBlueprints/twoNumbers.jbp")
def multiplication(payload):
	response = payload['operand1'] * payload['operand2']
	return str(response)


@app.route("/divide", methods=["POST"])
@deserializeJSON("jsonBlueprints/twoNumbers.jbp")
def division(payload):
	response = payload['operand1'] / payload['operand2']
	return str(response)

#------------------------------------------------------------

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)

