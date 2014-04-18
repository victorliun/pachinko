
from flask import Flask
from flask import Flask, session, redirect, url_for, escape, request
from flask import render_template
import os
from functools import update_wrapper
from datetime import timedelta
from flask import make_response, request, current_app
from connectMongo import DBConnection
from connectMongoCrawler import DBCrawlerConnection
import json
from encoder import Encoder
from bson import json_util

app = Flask(__name__)
app.secret_key = os.urandom(24)
dbConn = DBConnection()
dbConn1 = DBCrawlerConnection()

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
		#return 'Logged in as %s' % escape(session['username'])
		return render_template('showLinks.html')
	return 'You are not authorised to log in. Please enter correct username and password.'

@app.route('/login', methods=['GET', 'POST'])
def login():
	if(request.method == 'POST'):
		print request.form['password']
		if(request.form['username'] == 'app' and request.form['password'] == 'password'):
			session['username'] = request.form['username']
		return redirect(url_for('home'))
	return render_template('login_page.html')

@app.route('/logout')
def logout():
	# remove the username from the session if it's there
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/home')
def home():
	return redirect(url_for('analysis'))#render_template('home.html')

@app.route('/analysis')
def analysis():
    return render_template('get_data.html')

@app.route('/set-crawler')
def set_crawler():
    return render_template('set_crawler.html')

@app.route('/update')
def update():
    return render_template('update_hall_and_machine.html')



@app.route('/viewData')
def viewData():
	return render_template('single_viewdata.html')

from collections import defaultdict


def getSpinCount(data):
    	c_cnt = defaultdict(int)
	c_max = defaultdict(int)
	c_max_time = {}
	c_max_time_win = {}
	renchan_wins = defaultdict(list)
	renchan_count = defaultdict(int)
	totalwins = defaultdict(int)
	ret = []
	for post in data:
		dt = post["date"]
		if dt not in c_max_time:
			c_max_time[dt] = ""
		c_cnt[dt] += post["spin_count_of_win"]
		if len(post["time_of_win"]) > 3:
			if post["win_number"] != "--" and c_max[dt] < post["win_number"]:
				c_max[dt] = post["win_number"]
			if post["time_of_win"] != "--" and c_max_time[dt] < post["time_of_win"]:
				c_max_time[dt] = post["time_of_win"]
		if post["time_of_win"] == "--" and post["win_number"] == "--":
			c_max_time_win[dt] = post["spin_count_of_win"]
		if post["renchan"] == 0 and post["win_number"] != "--":
			renchan_wins[dt].append({"time":post["time_of_win"], "spin": post["spin_count_of_win"]})
		if post["renchan"] > 0:
			renchan_count[dt] += post["renchan"]
		if post["win_number"] > totalwins[dt] and totalwins[dt] != -1:
			totalwins[dt] = post["win_number"]
		if post["win_number"] == "--":
			totalwins[dt] = 0
			
	for c in sorted(c_cnt.keys()):
		r = {}
		r["date"] = c
		r["time_of_win"] = ""
		r["value"] = c_cnt[c]
		r["max_win_number"] = c_max[c]
		r["closingspincount"] = c_max_time_win[c]
		r["singlewinsspincount"] = renchan_wins[c]
		r["renchan"] = renchan_count[c]
		if totalwins[dt] == -1:
			r["totalwins"] = 0
		else:
			r["totalwins"] = totalwins[c]

		ret.append(r)
	return ret

@app.route('/Data')
@crossdomain(origin='*')
def getData():
    startDate = request.args.get('startDate', '')
    endDate = request.args.get('endDate', '')
    hallcode = request.args.get('hallcode', '')
    machinetype = request.args.get('machinetype', '')
    machinenumber = request.args.get('machinenumber', '')
    chartType = request.args.get('chart', '')
    posts= dbConn.getData(startDate,endDate,hallcode,machinetype,machinenumber)
    list = []
    spincount = []
    if len(chartType) > 0:
	    spincount = getSpinCount(posts)
    if chartType == 'spincount':
    	list = spincount
    elif chartType == 'winspincount':
	for s in spincount:
		rec = {}
		rec["date"] = s["date"]
		rec["value"] = float(s["value"])/s["max_win_number"]
		rec["time_of_win"] = ""
		list.append(rec)
    elif chartType == "closingspincount":
	for s in spincount:
		rec = {}
		rec["date"] = s["date"]
		rec["time_of_win"] = ""
		rec["value"] = s["closingspincount"]
		list.append(rec)
    elif chartType == 'singlewinsspincount':
    	for s in spincount:
		for l in s["singlewinsspincount"]:
			rec = {}
			rec["date"] = s["date"]
			rec["time_of_win"] = l["time"]
			rec["value"] = l["spin"]
			list.append(rec)
    elif chartType == "renchan":
    	for s in spincount:
		rec = {}
		rec["date"] = s["date"]
		rec["time_of_win"] = ""
		rec["value"] = s["renchan"]
		list.append(rec)
    elif chartType == "totalwins":
    	for s in spincount:
		rec = {}
		rec["date"] = s["date"]
		rec["time_of_win"] = ""
		rec["value"] = s["totalwins"]
		list.append(rec)
    else:
    	for post in posts:
		list.append(post)
    #return json.dumps(list, cls=Encoder)
    return json.dumps(list, default=json_util.default)

@app.route('/get_machine_type_details')
@crossdomain(origin='*')
def get_machine_type_details():
    startDate = request.args.get('startDate', '')
    endDate = request.args.get('endDate', '')
    hallcode = request.args.get('hallcode', '')
    machinetype = request.args.get('machinetype', '')
    res = []
    #print machines
    if hallcode and machinetype:
        res = summary_machine_data(startDate,endDate,hallcode,machinetype)
    elif hallcode and not machinetype:
        machine_types = dbConn.getMachineDetails("hallcode", hallcode, '','', "machine_type")
        for mach_type in machine_types:
            machine_datas = summary_machine_data(startDate,endDate,hallcode,mach_type)
            machine_type_data = {}
            machine_type_data['machine_type'] = mach_type
            machine_range = [ machine['range'] for machine in machine_datas]
            machine_type_data['range'] = int(round(reduce(lambda x,y: x+y, machine_range)/len(machine_range)))
            machine_winspin = [ machine['win_spin'] for machine in machine_datas]
            machine_type_data['win_spin'] = int(round(reduce(lambda x,y: x+y, machine_winspin)/len(machine_winspin)))
            machine_single_win = [ machine['single_win'] for machine in machine_datas]
            machine_type_data['single_win'] = int(round(reduce(lambda x,y: x+y, machine_single_win)/len(machine_single_win)))
            machine_renchan = [ machine['renchan'] for machine in machine_datas]
            machine_type_data['renchan'] = int(round(reduce(lambda x,y: x+y, machine_renchan)/len(machine_renchan)))
            machine_total_win = [ machine['total_win'] for machine in machine_datas]
            machine_type_data['total_win'] = int(round(reduce(lambda x,y: x+y, machine_total_win)))
            res.append(machine_type_data)

    return json.dumps(res, default=json_util.default)


def summary_machine_data(startDate,endDate,hallcode,machinetype):
    """
    This function will summary data from each machine.
    """
    res = []
    machines = dbConn.getMachineDetails("hallcode", hallcode, "machine_type",machinetype, "machine")
    for machine in machines:
        cllc = dbConn.get_collections(startDate,endDate,hallcode,machinetype,machine)
        length = len(cllc)
        resp = {}
        resp['machine'] = machine
        ranges = []
        for cl in cllc:
            if cl.has_key('machine_range') and cl['machine_range'] != '--':
                ranges.append(cl['machine_range'])
            elif cl.has_key('range') and cl['range'] != '--':
                ranges.append(cl['range'])
        if ranges:
            resp['range'] = int(round(reduce(lambda x,y: int(x)+int(y), ranges)/len(ranges)))
        else:
            resp['range'] = 0
        win_spins = [cl['spin_count_of_win'] for cl in cllc if cl['spin_count_of_win'] != '--']
        if win_spins:
            resp['win_spin'] = int(round(reduce(lambda x,y:x+y, win_spins)))
        else:
            resp['win_spin'] = 0
        
        single_wins = [cl['spin_count_of_win'] for cl in cllc \
            if cl['renchan'] == 0 and cl['spin_count_of_win'] != '--']
        if single_wins:
            resp['single_win'] = int(round(reduce(lambda x,y:x+y, single_wins)/len(single_wins)))
        else:
            resp['single_win'] = 0

        renchans = [cl['renchan'] for cl in cllc if cl['renchan'] != '--']
        if renchans:
            resp['renchan'] = reduce(lambda x,y:x+y, renchans)
        else:
            resp['renchan'] = 0
        totalwins = [cl['win_number'] for cl in cllc if cl['win_number'] != '--']
        if totalwins:
            resp['total_win'] = len(totalwins)
        else:
            resp['total_win'] = 0
        res.append(resp)
    return res

@app.route('/getHallcode/column=<column>')
@crossdomain(origin='*')
def getHallCode(column):
    posts= dbConn.getHallCode(column)
    list = []
    for post in posts:
        list.append(post)
    return json.dumps(list, cls=Encoder)

@app.route('/getMachineDetails')
@crossdomain(origin='*')
def getMachineDetails():
    column = request.args.get('column', '')
    value = request.args.get('value', '')
    column2 = request.args.get('column2', '')
    value2 = request.args.get('value2', '')
    distinctcol = request.args.get('distinctcol', '')
    posts= dbConn.getMachineDetails(column,value,column2,value2,distinctcol)
    list = []
    for post in posts:
        list.append(post)
    return json.dumps(list, default=json_util.default)

@app.route('/setCrawlerData', methods=['POST','GET'])
@crossdomain(origin='*')
def setCrawlerData():
    if(request.method == 'POST'):
        username= request.form['username']
        password= request.form['password']
        targetHallocde= request.form['targetHallocde']
        targetmachinetype= request.form['targetmachinetype']
        startFirstCrawlTime= request.form['startFirstCrawlTime']
        startLastCrawlTime= request.form['startLastCrawlTime']
        startingDate= request.form['startingDate']
        finishingDate= request.form['finishingDate']
        dbConn1.setCrawlerData(username,password,targetHallocde,targetmachinetype,startFirstCrawlTime,startLastCrawlTime,startingDate,finishingDate)	
	#return json.dumps({ "result" : "Data Submitted suuceessfully"})
	msg = "Data saved successfully."
        return render_template('set_crawler_parameters.html', msg=msg)
    #username = request.args.get('username', '')
    return render_template('set_crawler_parameters.html', msg="")

@app.route('/getCrawlerData', methods=['POST','GET'])
@crossdomain(origin='*')
def getCrawlerData():
    posts= dbConn1.getLatestCrawlerDetails()
    list = []
    for post in posts:
        list.append(post)
    return json.dumps(list, default=json_util.default)

@app.route('/getPreviousData', methods=['POST','GET'])
@crossdomain(origin='*')
def getPreviuosData():
    posts= dbConn1.getPreviousData()
    list = []
    for post in posts:
        list.append(post)
    return json.dumps(list, default=json_util.default)


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
