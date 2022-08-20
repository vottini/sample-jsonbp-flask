# Using [jsonbp](https://github.com/vottini/jsonbp) with Flask

This sample shows a possible way to use [jsonbp](https://github.com/vottini/jsonbp) inside a Flask application. It consists of accepting a JSON with two decimal numbers and offers the four basic arithmetic (+, -, ×, ÷) operations as service endpoints.

The JSON blueprint is thus:

```
root {
	operand1: decimal,
	operand2: decimal
}
```
which in this sample project is saved inside the directory _"jsonBlueprints"_ as the file _"twoNumbers.jbp"_. In the end, we'll come to develop a mean of using jsonbp in the following way:

```py
@app.route("/divide", methods=["POST"])
@deserializeJSON("jsonBlueprints/twoNumbers.jbp")
def division(payload):
	response = payload['operand1'] / payload['operand2']
	return str(response)
```

## Installation

```bash
$ python3 -m venv .environment
(.environment) $ source .environment/bin/activate
(.environment) $ pip3 install Flask jsonbp
```

## Running

### Server

In the same terminal where you sourced the activate script of venv, run the server by issuing:
```bash
(.environment) $ python3 main.py
```

### Requester

This sample comes with a simple shell script _request.sh_ that calls curl with the right parameters. Open a new terminal, navigate to the sample directory, and issue requests to the server by running this script:

```bash
$ ./request.sh
Usage: ./request.sh <operation> <number> <number>
Where <operation> can be:
- plus
- minus
- times
- divide

$. /request.sh plus 2 2
4.00
```

## Souce analysis

This sample is explained in 3 steps, where we'll incrementaly improve the ease of use of jsonbp along Flask.

### Step #1 - Straight Method

Initially, let us just see how one can use jsonbp in a Flask annotated function without giving much thought in how to make it less monolithic. 

First of all, we must load the blueprint that declares the operands. Then, during the response processing, we need to get the raw string sent to Flask inside the POST request. We feed this string directly to jsonbp's blueprint instance, which will return either if deserialization was successful or not. If not, we prepare and return a response with status code 400 (bad request) whose content is a string informing what was the problem. When the payload is ok, we simply do the respective operation (add the numbers in this case) and return the result.

```py
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
	
``` 

### Step #2 - Using Decorators

Now this same flow can be applied to most requests. For starters, we can create a function that retrieves the string from the current request and a function that creates bad responses. Then, in the same veins as Flask, we can define a decorator to wrap the checking if the payload is valid or not, and to automatically dispatch bad responses whenever deserialization fails, like this:

```py
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
	
```

Then we can simply decorate the real core functionality, which must be a function that receives at least one parameter (the deserialized payload) and returns the appropriate response. This function doesn't then need to have any verification code boilerplate, it can simply trust that the payload obeys the blueprint definition. Note that our decorator must come **after** the Flask route decorator:

```py
@app.route("/minus", methods=["POST"])
@feedJSON
def subtraction(payload):
	response = payload['operand1'] - payload['operand2']
	return str(response)
	
```

### Step #3 - Parameterize the decorator

And finally, we can go a step further and parameterize the decorator itself to accept a path to the file which has the blueprint content. Moreover, we use _functools.wraps()_ to restore the wrapped function metadata, and make our _wrap()_ function well behaved by accepting any kind of parameters and passing it along to the wrapped function, such that arguments besides our payload can be received.

```py
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
```
By doing this, we can now easily add verification to Flask decorated functions by specifying the json schema that requests sent to them must comply to.

```py
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
	
```

**Obs**: It should be noted that there is no meaningful performance loss repeating the same blueprint file in more than one decorator like above. jsonbp registers the absolute path of blueprints it has parsed, so requesting again the blueprint from a previously parsed file should yield an already cached result.
