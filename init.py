#!/usr/bin/env python

from flask import Flask, request, jsonify
from functools import wraps
from os import path
from time import asctime as localtime

import logging
import ecmanaged.loadb

app = Flask(__name__)
ecm = ecmanaged.loadb.ECMLoadBalancer()

# Logger
cwd = path.dirname(path.abspath( __file__ ))
file_handler = logging.FileHandler(cwd + '/loadb_api.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

# Read secret
SECRET = ecm.secret_read()

def output_json(data, code = 200, headers=None):
	message = {
		'status': code,
		'message': data,
		}
	resp = jsonify(message)
	resp.status_code = code
	resp.headers.extend(headers or {})

	# Log event
	log_str = '%s (%s): request: %s - data: %s' % (localtime(),request.method,request.url,data)
	if code == 200:   app.logger.info   ('INFO - %s' % log_str)
	elif code >= 500: app.logger.error  ('WARN - %s' % log_str)
	elif code >= 400: app.logger.warning('CRIT - %s' % log_str)

	return resp

def check_auth(username, password):
	return username == 'admin' and password == SECRET

def authenticate(msg):
	headers = {}
	headers['WWW-Authenticate'] = 'Basic realm="private"'
	return output_json(msg,401,headers)

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth:
			return authenticate("Authenticate")

		elif not check_auth(auth.username, auth.password):
			return authenticate("Authentication failed")
		return f(*args, **kwargs)

	return decorated


@app.errorhandler(404)
def output_not_found(error=None):
	return output_json('Not Found: ' + request.url, 404)

@app.errorhandler(500)
def output_error(error=None):
	return output_json('Error: ' + str(error), 500)

#
# API Resources
#

@app.route('/', methods=['GET',])
def config_get():
	return output_json(ecm.config_get())

@app.route('/config/', methods=['POST',])
@app.route('/main/', methods=['POST',])
@requires_auth
def config_set():
	retval = None
	if request.method == 'POST':
		section = str(request.url_rule).replace('/','')
		retval = ecm.config_set(request.json,section)

	return output_json(retval)

@app.route('/service/<id>/', methods=['GET','POST','DELETE'])
@requires_auth
def service_id(id = None):
	retval = None
	if request.method == 'GET':
		retval = ecm.service_get(id)

	elif request.method == 'POST':
		retval = ecm.service_add(id,request.json)

	elif request.method == 'DELETE':
		retval = ecm.service_delete(id)

	return output_json(retval)

@app.route('/service/<id>/<node>/', methods=['GET','POST','DELETE'])
@requires_auth
def node(id=None, node=None):
	retval = None
	if request.method == 'GET':
		retval = ecm.node_get(id,node)

	elif request.method == 'POST':
		retval = ecm.node_add_into_service(id,node,request.json)

	elif request.method == 'DELETE':
		retval = ecm.node_delete_from_service(id,node)

	return output_json(retval)

if __name__ == '__main__':
	app.run(port=5002, debug=True)

