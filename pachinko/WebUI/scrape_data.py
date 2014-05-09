from ghost import Ghost
import logging
import time
import urllib2,time,re
import traceback
import json
from scrapy.selector import HtmlXPathSelector
from functools import wraps
from datetime import datetime, timedelta
from pymongo import Connection
from connectMongo import DBConnection 

logger = logging.getLogger("ghost")
logging.basicConfig(level=logging.DEBUG)
import time

from utils import *

import connectMongoCrawler as cmc

meta_data_l = cmc.DBCrawlerConnection().getLatestCrawlerDetails()
meta_data = {}
for md in meta_data_l:
    meta_data = md


# if the time of current day is before than 6:00pm then the data is still
# belongs yesterday. So make it to yesterday, if time is between 0:00am ~ 6:00am
now = datetime.now()
six_clock = now.replace(hour=6,minute=0,second=0)
if now < six_clock:
    now = now - timedelta(days=1)
today_date = now.strftime("%Y-%m-%d")

hall_code = meta_data["targetHallocde"]
machine_type = meta_data["targetmachinetype"].split(",")

username = meta_data["username"]
password = meta_data["password"]


loaded_machines = {}

def getNextMachine(ghost):
    print loaded_machines, len(loaded_machines)
    js = """
    var done = """ + json.dumps(loaded_machines.keys()) + """;
    var buttons = document.getElementsByTagName('a');
    var clicked_href = {};
    var qwe = 100;
    for(var i=0; i<buttons.length; i++){
        if(buttons[i].href.indexOf("tableHistoryClick") != -1){
                if(done.indexOf(buttons[i].href) == -1){
                        qwe = buttons[i].href;
                        break;
                }
        }
    } 
    qwe;
    """
    print js
    result, resources = ghost.evaluate(js)
    print "extracted machinetype", result
    loaded_machines[str(result)] = 1
    return result

def getData(gh, hallcode, machine_range):
    con = Connection()
    content = unicode(gh.content)
    hxs = HtmlXPathSelector(text=unicode(gh.content))
    rows = hxs.select('//table//tr').extract()
    machine = ""
    try:
        machine2 = hxs.select('//div[@id="dedama_past_table"]//h4/text()').extract()[0]
    except:
        return
    for m in machine2:
        try:
            int(m)
            machine += m
        except:
            pass
    dump = {}
    dump["timestamp"] = datetime.now()
    dump["hallcode"] = hallcode
    modelClick = re.search(r'modelClick\((.*)\);', content, re.M|re.I)
    modelClick = modelClick.group().split(",")
    modelClick = modelClick[1].strip()
    modelClick = re.search(r'([0-9]+)', modelClick)
    modelClick = modelClick.group().strip()
    machine_type = modelClick
    print "machine_set", machine_type
    dump["machine_type"] = modelClick
    dump["machine"] = machine
    dump["date"] = today_date
    dump["machine_range"] = machine_range
    jackpots = []
    i = 0

    for r in rows:
        if i == 0:
            i = 1
            continue
        res = {}
        res["timestamp"] = datetime.now()
        res["hallcode"] = hallcode
        res["machine_type"] = machine_type
        res["machine"] = machine
        res["date"] = today_date
        res["renchan"] = 0
        res["machine_range"] = machine_range
        hxs2 = HtmlXPathSelector(text=r)
        cells = hxs2.select('//td/text()').extract() + hxs2.select('//th/text()').extract()
        jr = []
        res["win_number"] = cells[0].strip()
        if "*" in res["win_number"]:
            res["renchan"] = 1
        else:
            res["renchan"] = 0
        try:
            res["win_number"] = int(res["win_number"].replace("*", "").strip())
        except:
            res["win_number"] = 0
        try:
            res["column5"] = cells[4].strip()
        except:
            pass
        time_of_win = cells[1].strip()
        if time_of_win == "--":
            time_of_win = "NaN"
        res["time_of_win"] = time_of_win
        res["spin_count_of_win"] = cells[2].strip()
        try:
            res["spin_count_of_win"] = int(cells[2].strip())
        except:
            res["spin_count_of_win"] = 0

        try:
            res["total_balls_out"] = int(cells[3].strip())
        except:
            res["total_balls_out"] = 0

        for c in cells:
            jr.append(c.strip())
        
        jackpots.append(jr)
        key = {}
        key["hallcode"] = hallcode
        key["machine"] = machine
        key['machine_type'] = machine_type
        key["date"] = today_date
        key["time_of_win"] = time_of_win
        print "saving ", res

        one_record = con['pachinko_data2']['data'].find_one(key)
        if not one_record:
            records_of_the_date = con['pachinko_data2']['data'].find({
                "hallcode":hallcode,
                "machine":machine,
                "machine_type":machine_type,
                "date":today_date,
                })
            highest_range = get_highest_range(records_of_the_date)
            if machine_range < highest_range:
                res['machine_range'] = highest_range
            con["pachinko_data2"]["data"].update(key, res, upsert=True)
        elif time_of_win == 'NaN':
            con["pachinko_data2"]["data"].update(key, res, upsert=True)
        #save hallcode, machine_type, machine if one is new
        mdb = DBConnection()
        if not mdb.machine_details.find({'hallcode':hallcode}):
            mdb.insert_hallcode(hallcode)
        if not mdb.machine_details.find({'machine_type':machine_type, 'ancestors':[hallcode]}):
            mdb.set_machine_type(hallcode, machine_type)
        if not mdb.machine_details.find({'machine':machine, 'ancestors':[hallcode, machine_type]}):
            mdb.insert_machine(hallcode, machine_type, machine)
    dump["series"] = jackpots
    con["pachinko_dump2"]["data"].insert(dump)

def get_highest_range(records):
    """
    This function exist because the range in db is stored as string, unbelievable.
    So have to write an function to get highest string range
    """

    highest_range = 0
    for record in records:
        this_range = record.get('machine_range', 0)
        try:
            this_range = int(this_range)
        except ValueError, ver:
            this_range = 0
        if this_range > highest_range:
            highest_range = this_range
    return highest_range

    
def sign_in(gh, account_id, account_ps):
    """
    Check yahoo account name and password if it is correct
    """
    try:
        page, resources = gh.open("http://fe.site777.tv/data/yahoo/login.php")
        print page.url 
        gh.wait_for_selector('input[name=login]')
        result, resources = gh.set_field_value("input[name=login]", account_id) #"gopachipro")
        result, resources = gh.set_field_value("input[name=passwd]", account_ps) #"pachi.pro.2014")
        result, resources = gh.click(".btnLogin", expect_loading=True)
        print 2
        time.sleep(2)
    
        result, resources = gh.evaluate("document.forms[0].submit();", expect_loading=True)
        time.sleep(3)
        print 3
        result, resources = gh.evaluate("document.forms[0].submit();", expect_loading=True)
        time.sleep(4)
        print 4
        result, resources = gh.evaluate("document.forms[0].submit();", expect_loading=True)
        print result.url
        if 'yahoo' in str(result.url):
            print "login failed."
            return False,
        else:
            print "loged in!."
            return True, result, resources
    except Exception, terr:
        logging.error(terr)
        return

def start_crawling(hallcode=hall_code, machine_types=machine_type,
         account_id=username, account_ps=password):
    """start_crawling"""
    
    logging.warning("%s,%s,%s,%s" %(hallcode, machine_types, account_id, account_ps))
    gh = Ghost(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36", wait_timeout=100);
    loged = sign_in(gh, account_id, account_ps)
    if not loged[0]:
        gh.exit()
        return
    result = loged[1]
    time.sleep(2)
    u = "/".join(str(result.url).split("/")[:-1]) + "/" + "HallSelectLink.do?hallcode=" + hallcode
    print u

    
    result, resources = gh.open(u)
    button_index = 0

    machine_type_condition = ["buttons[i].getAttributeNode('onclick').value.indexOf('" + mt.strip() + "') != -1"  for mt in machine_types]
    machine_condition = ""
    if len(machine_type_condition) > 0:
        machine_condition = " || ".join(machine_type_condition)
    machine_condition = " && ( " + machine_condition + " )"
    
    print machine_condition
    save_next_crawling_time()
    while True:
        js = """
        var qwe = -1;
        var buttons = document.getElementsByTagName('input');
        for(var i=""" + str(button_index) + """; i<buttons.length; i++){
        try{
            if(buttons[i].name == "select" """ + machine_condition + """){
                qwe = i;    
                break;
            }
        } catch(err) {
        }
        }
        qwe;
        """

        result, resources = gh.evaluate(js)
        button_index = result
        if button_index == -1:
            break
        print "extracted index of machine set:", result


        js = """
        var buttons = document.getElementsByTagName('input');
        for(var i=""" + str(button_index) + """; i<buttons.length; i++){
        try{
            if(buttons[i].name == "select" """ + machine_condition + """){
                if(i == """ + str(button_index) + """)
                    buttons[i].click();
                    break;
            }
        } catch(err) {
        }
        } """
        print js
        result, resources = gh.evaluate(js, expect_loading=True)
        print "###result,", result.url

        goToMachines(gh, hallcode)
        button_index += 1
        js = """
        history.go(-1);
        """
        result, resources = gh.evaluate(js, expect_loading=True)

    gh.exit()
    print "ghost exits."

def save_next_crawling_time():
    """save next crawling time"""
    form = json.loads(read_form())
    now = datetime.now()
    if now.minute < 55:
        plus = 55 - now.minute
    else:
        plus = 60 - (now.minute - 55)
    next_run_time = now + timedelta(minutes=plus)
    form['next_run_time'] = next_run_time.strftime("%Y/%m/%d %H:%M")
    save_form(json.dumps(form))


def goToMachines(gh, hallcode):
    res = 0
    if True:
        hxs = HtmlXPathSelector(text=gh.content)
        open("b", "wb").write(gh.content.encode("utf-8", "ignore"))
        complete_table = hxs.select('//div[@id="ata0"]').extract()
        try:
            complete_table = complete_table[0]
        except:
            return
        hxs2 = HtmlXPathSelector(text=complete_table)
        s = hxs2.select('//table//tr').extract()

        for tr in s:
            hxs3 = HtmlXPathSelector(text=tr)
            js_link = hxs3.select('//span[@class="his"]/a/@href').extract()

            print "####machine ", hxs3.select('//span[@class="num"]/text()').extract()
            if len(js_link) > 0:
                machine_range = hxs3.select('//td[5]/text()').extract()
                js_link = js_link[0]
                if "tableHistoryClick" in js_link:
                    if len(machine_range) > 0:
                        try:
                            int (machine_range[0])
                            machine_range = machine_range[0]
                        except ValueError, ve:
                            machine_range = ""
                    else:
                        machine_range = ""
                    js_link = js_link.replace("javascript:", "")
                    print "executing:", js_link
                    result, resources = gh.evaluate(js_link, expect_loading=True)
                    getData(gh, hallcode, machine_range)
                    print "#####machine_range,", machine_range
                    js = """
                    history.go(-1);
                    """
                    result, resources = gh.evaluate(js, expect_loading=True)
                    time.sleep(2)

def goToMachines_vc(ghost):
    res = 0
    while True:
        res = getNextMachine(ghost)
        if "javascript" in str(res):
            js = """
            var a = \"""" + str(res) + """\";
            var buttons = document.getElementsByTagName('a');
            var clicked_href = {};
            for(var i=0; i<buttons.length; i++){
            if(buttons[i].href.indexOf("tableHistoryClick") != -1){
                if(a == buttons[i].href){
                    buttons[i].click();
                    break;
                }
            }
            } """
            result, resources = ghost.evaluate(js, expect_loading=True)
            getData(ghost, hall_code)
            js = """
            history.go(-1);
            """
            result, resources = ghost.evaluate(js, expect_loading=True)
            time.sleep(2)
        else:
            break

if __name__=="__main__":
    start_crawling()
    
