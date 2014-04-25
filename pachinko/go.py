from ghost import Ghost
import logging
import time
import urllib2,time,re
import traceback
import json
from scrapy.selector import HtmlXPathSelector
from functools import wraps
from datetime import datetime
from machine import *
from pymongo import Connection
 
logger = logging.getLogger("ghost")
logging.basicConfig(level=logging.DEBUG)
import time

today_date = time.strftime("%Y-%m-%d")
hall_code = "27081001"
hall_code = "29008002"
machine_type = "024134"
machine_type = "023979"


def getData(g, hallcode):
    con = Connection()
    hxs = HtmlXPathSelector(text=unicode(g.content))
    rows = hxs.select('//table//tr').extract()
    machine = ""
    machine2 = hxs.select('//div[@id="dedama_past_table"]//h4/text()').extract()[0]
    for m in machine2:
        try:
        int(m)
            machine += m
    except:
        pass
    dump = {}
    dump["timestamp"] = datetime.now()
    dump["hallcode"] = hallcode
    dump["machine_type"] = machine_type
    dump["machine"] = machine
    dump["date"] = today_date
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
        pass
    try:
        res["column5"] = cells[4].strip()
    except:
        pass
    res["time_of_win"] = cells[1].strip()
    res["spin_count_of_win"] = cells[2].strip()
    try:
        res["spin_count_of_win"] = int(cells[2].strip())
    except:
        pass

    try:
        res["total_balls_out"] = int(cells[3].strip())
    except:
        try:
            res["total_balls_out"] = cells[3].strip()
        except:
            pass

    for c in cells:
        jr.append(c.strip())
    
    jackpots.append(jr)
        key = {}
    key["hallcode"] = hallcode
    key["machine"] = machine
    key["date"] = today_date
    key["time_of_win"] = cells[1].strip()
        con["pachinko_data2"]["data"].update(key, res, upsert=True)
    dump["series"] = jackpots
    con["pachinko_dump2"]["data"].insert(dump)


def signin():
    ghost = Ghost(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36", wait_timeout=100);
    page, resources = ghost.open("http://fe.site777.tv/data/yahoo/login.php")
    ghost.wait_for_selector('input[name=login]')
    
    result, resources = ghost.set_field_value("input[name=login]", "gopachipro")
    result, resources = ghost.set_field_value("input[name=passwd]", "pachi.pro.2014")
    result, resources = ghost.click(".btnLogin", expect_loading=True)
    print 2
    time.sleep(2)

    result, resources = ghost.evaluate("document.forms[0].submit();", expect_loading=True)
    time.sleep(3)
    print 3
    result, resources = ghost.evaluate("document.forms[0].submit();", expect_loading=True)
    time.sleep(4)
    print 4
    result, resources = ghost.evaluate("document.forms[0].submit();", expect_loading=True)
    print result.url
    if 'yahoo' in str(result.url):
        return
    time.sleep(2)
    u = "/".join(str(result.url).split("/")[:-1]) + "/" + "HallSelectLink.do?hallcode=" + hall_code
    print u
    #ghost.open("http://cs2.site777.tv/data/wE6pfoe9du115e0oh044r4ngd8tmb71agji4786e10/kakin/HallSelectLink.do?hallcode=27038046", expect_loading=True)
    result, resources = ghost.open(u)
    js = """
    var buttons = document.getElementsByTagName('input');
    for(var i=0; i<buttons.length; i++){
    try{
        if(buttons[i].name == "select" && buttons[i].getAttributeNode('onclick').value.indexOf('""" + str(machine_type) + """') != -1){
            buttons[i].click();
            break;
        }
    } catch(err) {
    }
    } """
    print js
    result, resources = ghost.evaluate(js, expect_loading=True)

    goToMachines(ghost)

def goToMachines(ghost):
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
    signin()
    
