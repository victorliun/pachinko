from __future__ import  absolute_import
from flask import Flask, g, session, redirect, \
        url_for, escape, request, render_template,\
        make_response, request, current_app
import os, signal, ast, json
import logging
from functools import update_wrapper
from datetime import timedelta
from connectMongo import DBConnection
from connectMongoCrawler import DBCrawlerConnection
from encoder import Encoder
from bson import json_util
from functools import wraps
from ghost import Ghost
from utils import *
from scrape_data import start_crawling
import urllib
from datetime import datetime
import threading
from multiprocessing import Process
import itertools
from settings import *
from session import MongoSessionInterface
app = Flask(__name__)
app.secret_key = os.urandom(24)
dbConn = DBConnection()
dbConn1 = DBCrawlerConnection()
# enable session
app.session_interface = MongoSessionInterface(db='pachinko_systems')#, uri=MONGOHQ_URI)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.after_request
def update_sessions(response):
    ignore_list = ('/static', '/login','/logout',
            "/getHallcode", '/getMachineDetails', 
            "/check_yahoo_account",)
    url_rule = request.url_rule
    if url_rule and request.method == 'GET':
        rule = url_rule.rule
        if rule == '/':
            return response
        if not rule.startswith(ignore_list): 
            if rule.startswith(('/Data', '/get_machine_type_details')):
                session['args'] = request.args.to_dict()
            else:
                session['url'] = rule
                session['endpoint'] = url_rule.endpoint 
                session['args'] = request.args.to_dict()
            session.modified = True
    return response


def get_next_run_time():
    """return next next_run_time"""
    now = datetime.now()
    if now.minute < 55:
        plus = 55 - now.minute
    else:
        plus = 60 - (now.minute - 55)
    next_run_time = now + timedelta(minutes=plus)
    return next_run_time.strftime("%Y/%m/%d %H:%M")

@app.before_request
def before_request():
    """
    pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'username' in session:
        g.user = session['username']

  
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
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        if(request.form['username'] == 'app' and request.form['password'] == 'password'):
            session['username'] = request.form['username']
            next = request.args.get('next')
            endpoint = session.get('endpoint','')
            if endpoint:
                return redirect(url_for(endpoint, message=session.get('args')))
            elif not next:
                next = '/home'
            else:
                next = next.split('/',3)[-1]
            return redirect(next)
    return render_template('login_page.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return redirect(url_for('analysis'))#render_template('home.html')

@app.route('/analysis')
@login_required
def analysis():
    message = request.args.get('message')
    if message:
        message = ast.literal_eval(message)
    return render_template('get_data.html', message=message)

@app.route('/set-crawler', methods=['POST','GET'])
@login_required
def set_crawler():
    if request.method == "GET":
        if not os.path.exists('crawler_last_setting.json'):
            clean_form()
        form = read_form()
        form = json.loads(form)
        return render_template('set_crawler.html', form=form)

    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        target_hallcode = request.form['target_hallcode']
        target_machine_types = request.form['target_machine_types']
        switch = request.form['signal']
        res = {}
        form_dict = {}
        form_dict['username'] = username
        form_dict['password'] = password
        form_dict['target_hallcode'] = target_hallcode
        form_dict['target_machine_types'] = target_machine_types
        form_dict['signal'] = switch
        form_dict['next_run_time'] = get_next_run_time()
        if switch == "START":
            logging.warning("start crawling:")
            #target_machine_types = filter(lambda x: x,target_machine_types.split(','))  
            dbConn1.save_crawler_data(username, password, target_hallcode, target_machine_types)
            save_form(json.dumps(form_dict))
            start_cron()
            res['status'] = "Start crawling"
            res['next_run_time'] = form_dict['next_run_time']
            th = Process(target=start_crawling, args = (target_hallcode, target_machine_types, username, password))
            th.start()
            with open("scrape.pid", 'w+') as fi:
                print "start process:", th.pid
                fi.write(str(th.pid))
        elif switch == "STOP":
            logging.warning("stop crawling")
            clean_form()
            with open("scrape.pid", 'r') as fo:
                pid = fo.read()
                print "kill pid", pid
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except Exception, err:
                        logging.warning(err)
            stop_cron()
            res['status'] = "Stop crawling"
            res['next_run_time'] = ''
        return json.dumps(res)

@app.route('/update')
@login_required
def update():
    return render_template('update_hall_and_machine.html')

@app.route('/view-graphs')
@login_required
def view_grahps():
    message = request.args.get('message')
    if message:
        message = ast.literal_eval(message)
    return render_template('view_machine_graphs.html', message=message)


@app.route('/viewData')
@login_required
def viewData():
    return render_template('single_viewdata.html')

from collections import defaultdict


def getSpinCount(data):
    c_cnt = defaultdict(int)
    c_max = defaultdict(int)
    c_max_time = defaultdict(int)
    c_max_time_win = defaultdict(int)
    renchan_wins = defaultdict(list)
    renchan_count = defaultdict(int)
    totalwins = defaultdict(int)
    ret = []
    for post in data:
        dt = post["date"]
        try:
            c_cnt[dt] += int(post["spin_count_of_win"])
        except ValueError, err:
            pass

        if len(post["time_of_win"]) > 3:
            if post["win_number"] != 0 and c_max[dt] < post["win_number"]:
                c_max[dt] = post["win_number"]
            if post["time_of_win"] != "NaN" and c_max_time[dt] < post["time_of_win"]:
                c_max_time[dt] = post["time_of_win"]
        if post["time_of_win"] == "NaN" and post["win_number"] == 0:
            c_max_time_win[dt] = post["spin_count_of_win"]
        if post["renchan"] == 0 and post["win_number"] != 0:
            renchan_wins[dt].append({"time":post["time_of_win"], "spin": post["spin_count_of_win"]})
        if post["renchan"] > 0:
            renchan_count[dt] += post["renchan"]
        if post["win_number"] != 0:
            totalwins[dt] += 1
            
    for c in sorted(c_cnt.keys()):
        r = {}
        r["date"] = c
        r["time_of_win"] = ""
        r["value"] = c_cnt[c]
        r["max_win_number"] = c_max.get(c, '')
        r["closingspincount"] = c_max_time_win.get(c, '')
        r["singlewinsspincount"] = renchan_wins.get(c, '')
        r["renchan"] = renchan_count.get(c, '')
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
    limit = 100
    if machinenumber :
        limit = 0
    posts= dbConn.getData(startDate,endDate,hallcode,machinetype,machinenumber,limit)
    lst = []
    spincount = []
    if len(chartType) > 0:
        spincount = getSpinCount(posts)
    if chartType == 'spincount':
        lst = spincount
    elif chartType == 'winspincount':
        for s in spincount:
            rec = {}
            rec["date"] = s["date"]
            if s.get("max_win_number"):
                rec["value"] = float(s["value"])/s["max_win_number"]
            else:
                rec["value"] = s['value']
            rec["time_of_win"] = ""
            lst.append(rec)
    elif chartType == "closingspincount":
        for s in spincount:
            rec = {}
            rec["date"] = s["date"]
            rec["time_of_win"] = ""
            rec["value"] = s["closingspincount"]
            lst.append(rec)
    elif chartType == 'singlewinsspincount':
        for s in spincount:
            for l in s["singlewinsspincount"]:
                rec = {}
                rec["date"] = s["date"]
                rec["time_of_win"] = l["time"]
                rec["value"] = l["spin"]
                lst.append(rec)
    elif chartType == "renchan":
        for s in spincount:
            rec = {}
            rec["date"] = s["date"]
            rec["time_of_win"] = ""
            rec["value"] = s["renchan"]
            lst.append(rec)
    elif chartType == "totalwins":
        for s in spincount:
            rec = {}
            rec["date"] = s["date"]
            rec["time_of_win"] = ""
            rec["value"] = s["totalwins"]
            lst.append(rec)
    else:
        #CASE: Analysis page
        for post in posts:
            lst.append(post)
        if machinenumber and machinetype and hallcode:
            lst = add_cash_payout(lst)

    #return json.dumps(lst, cls=Encoder)
    return json.dumps(lst, default=json_util.default)


@app.route('/get_machine_type_details')
@crossdomain(origin='*')
def get_machine_type_details():
    """
    This function will return machine type data as a summary.
    """
    startDate = request.args.get('startDate', '')
    endDate = request.args.get('endDate', '')
    hallcode = request.args.get('hallcode', '')
    machinetype = request.args.get('machinetype', '')
    res = []
    #print machines
    if hallcode and machinetype:
        res = summary_machine_data(startDate,endDate,hallcode,machinetype)
    elif hallcode and not machinetype:
        machine_types = dbConn.get_machine_types(hallcode, True, startDate, endDate)
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
    machines = dbConn.get_machines(hallcode, machinetype, True, startDate, endDate)

    for machine in machines:
        cllc = dbConn.get_collections(startDate,endDate,hallcode,machinetype,machine)
        cllc = add_cash_payout(cllc)
        resp = {}
        resp['machine'] = machine
        date_range = 0
        ## calcuate range for this date range. It should be an average based on 
        ## the single highest range of the day 
        max_ranges = []
        win_spins = []
        totalwins = 0
        single_wins  = []
        cash_result = 0
        total_renchan_win = 0
        for the_date, records in itertools.groupby(cllc, lambda x: x['date']):
            date_range += 1
            max_range = 0

            for record in records:
                machine_range = record.get('machine_range', 0)
                try:
                    machine_range = int(machine_range)
                except ValueError, verr:
                    machine_range = 0
                if max_range < machine_range:
                    max_range = machine_range

                # spin count of win
                spin_count_of_win = record.get('spin_count_of_win', 0)
                try:
                    spin_count_of_win = int(spin_count_of_win)
                except ValueError, verr:
                    spin_count_of_win = 0
                win_spins.append(spin_count_of_win)

                # spin count of win
                spin_count_of_win = record.get('spin_count_of_win', 0)
                try:
                    spin_count_of_win = int(spin_count_of_win)
                except ValueError, verr:
                    spin_count_of_win = 0
                win_spins.append(spin_count_of_win)
                if record['win_number'] not in ('--', 0):
                    totalwins += 1

                if record['renchan'] == 0 and record['spin_count_of_win'] != '--':
                    single_wins.append(spin_count_of_win)

                if record['win_number'] in ('--', 0 ) and record['time_of_win'] == 'NaN':
                    cash_result += record['cash_result']

                if record['renchan'] == 1:
                    total_renchan_win += 1
            max_ranges.append(max_range)

        if max_ranges:
            resp['range'] = int(round(reduce(lambda x,y: x+y, max_ranges)/len(max_ranges)))
        else:
            resp['range'] = 0

        if win_spins and not totalwins == 0:
            resp['win_spin'] = int(round(reduce(lambda x,y:x+y, win_spins)/totalwins))
        else:
            resp['win_spin'] = 0    
        if single_wins:
            resp['single_win'] = int(round(reduce(lambda x,y:x+y, single_wins)/len(single_wins)))
        else:
            resp['single_win'] = 0

        resp['renchan'] = total_renchan_win
        resp['total_win'] = totalwins
        resp['cash_result'] = cash_result
        resp['average_cash_result'] = round(cash_result*1.0/date_range, 1)
        res.append(resp)
    return res

@app.route('/get_codes')
def get_codes():
    """
    this view will return hallcodes if no request args,
    machine types if only hallcode specified,
    machines if both hallcode and machinetype specified.
    """
    mdb = DBConnection()
    hallcode = request.args.get("hallcode")
    machinetype = request.args.get("machinetype")
    if not hallcode and not machinetype:
        return json.dumps(mdb.get_hallcodes(), default=json_util.default)
    elif hallcode and not machinetype:
        return json.dumps(mdb.get_machine_types(hallcode), default=json_util.default)
    elif hallcode and machinetype:
        return json.dumps(mdb.get_machines(hallcode, machinetype), default=json_util.default)

@app.route("/check_yahoo_account")
def check_yahoo_accout():
    """
    check yahoo accout is availale or not.
    """
    #password = request.args.get('password')
    username = request.args.get('username')
    url = "https://edit.yahoo.com/reg_json?PartnerName=yahoo_default&AccountID="+username+ "&ApiName=ValidateFields"
    res = urllib.urlopen(url).read()
    res = json.loads(res)
    return json.dumps(res)


@app.route('/getHallcode')
@crossdomain(origin='*')
def getHallCode():
    start_date = request.args.get('startDate', '')
    end_date = request.args.get('endDate', '')
    lst = dbConn.get_hallcodes(True, start_date, end_date)
    return json.dumps(lst, cls=Encoder)

@app.route('/getMachineDetails')
@crossdomain(origin='*')
def getMachineDetails():
    hallcode = request.args.get('hallcode', '')
    start_date = request.args.get('startDate', '')
    end_date = request.args.get('endDate', '')
    distinctcol = request.args.get('distinctcol', '')
    if distinctcol == 'machine_type':
        posts = dbConn.get_machine_types(hallcode, True, start_date, end_date)
    elif distinctcol == 'machine':
        machine_type = request.args.get('machine_type', '')
        posts = dbConn.get_machines(hallcode, machine_type, True, start_date, end_date)
    else:
        posts = []
    return json.dumps(posts, default=json_util.default)

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
        msg = "Data a saved successfully."
        return render_template('set_crawler_parameters.html', msg=msg)
    #username = request.args.get('username', '')
    return render_template('set_crawler_parameters.html', msg="")


@app.route('/getCrawlerData', methods=['POST','GET'])
@crossdomain(origin='*')
def getCrawlerData():
    posts= dbConn1.getLatestCrawlerDetails()
    lst = []
    for post in posts:
        lst.append(post)
    return json.dumps(lst, default=json_util.default)

@app.route('/getPreviousData', methods=['POST','GET'])
@crossdomain(origin='*')
def getPreviuosData():
    posts= dbConn1.getPreviousData()
    lst = []
    for post in posts:
        lst.append(post)
    return json.dumps(lst, default=json_util.default)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

