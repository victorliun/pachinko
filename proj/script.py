
from flask import Flask
from flask import Flask, session, redirect, url_for, escape, request
from flask import render_template
import os
from functools import update_wrapper
from datetime import timedelta
from flask import make_response, request, current_app
from connectMongo import DBConnection
import json
from encoder import Encoder
from bson import json_util

app = Flask(__name__)
app.secret_key = os.urandom(24)
dbConn = DBConnection()

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/')
def index():
	if 'username' in session:
		return 'Logged in as %s' % escape(session['username'])
	return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
	if(request.method == 'POST'):
		print request.form['password']
		if(request.form['username'] == 'app' and request.form['password'] == 'password'):
			session['username'] = request.form['username']
		return redirect(url_for('index'))
	return render_template('login.html')

@app.route('/logout')
def logout():
	# remove the username from the session if it's there
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route('/home')
def home():
	return render_template('index.html')

@app.route('/viewData')
def viewData():
	return render_template('single_viewdata.html')

@app.route('/Data/startDate=<startDate>/endDate=<endDate>')
@crossdomain(origin='*')
def getData(startDate,endDate):
    posts= dbConn.getData(startDate,endDate)
    list = []
    for post in posts:
	list.append(post)
    #return json.dumps(list, cls=Encoder)
    return json.dumps(list, default=json_util.default)

@app.route('/getHallcode/column=<column>')
@crossdomain(origin='*')
def getHallCode(column):
    posts= dbConn.getHallCode(column)
    list = []
    for post in posts:
        list.append(post)
    return json.dumps(list, cls=Encoder)

@app.route('/getMachineDetails/column=<column>/value=<value>/distinctcol=<distinctcol>')
@crossdomain(origin='*')
def getMachineDetails(column,value,distinctcol):
    posts= dbConn.getMachineDetails(column,value,distinctcol)
    list = []
    print 'sdsffeecc'
    for post in posts:
        list.append(post)
    return json.dumps(list, default=json_util.default)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
