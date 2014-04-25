from ghost import Ghost
import logging
import time
import urllib2,time,re
import traceback
import json
from scrapy.selector import HtmlXPathSelector
from functools import wraps
from datetime import datetime
from pymongo import Connection
from WebUI.connectMongo import DBConnection 
from WebUI.utils import sign_in

logger = logging.getLogger("ghost")
logging.basicConfig(level=logging.DEBUG)
import time

import WebUI.connectMongoCrawler as cmc

meta_data_l = cmc.DBCrawlerConnection().getLatestCrawlerDetails()
meta_data = {}
for md in meta_data_l:
    meta_data = md

today_date = time.strftime("%Y-%m-%d")

hall_code = "27081001"
hall_code = "29008002"
hall_code = meta_data["targetHallocde"]
machine_type = "024134"
machine_type = "023979"
machine_type = meta_data["targetmachinetype"].split(",")

username = meta_data["username"]
password = meta_data["password"]

print hall_code, machine_type, username, password

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
#   print res
    con["pachinko_data2"]["data"].update(key, res, upsert=True)
    dump["series"] = jackpots
    con["pachinko_dump2"]["data"].insert(dump)
    #save hallcode, machine_type, machine if one is new
    mdb = DBConnection()
    if not mdb.machine_details.find({'hallcode':hallcode}):
        mdb.insert_hallcode(hallcode)
    if not mdb.machine_details.find({'machine_type':machine_type, 'ancestors':[hallcode]}):
        mdb.set_machine_type(hallcode, machine_type)
    if not mdb.machine_details.find({'machine':machine, 'ancestors':[hallcode, machine_type]}):
        mdb.insert_machine(hallcode, machine_type, machine)


def start_crawling(hallcode=hall_code, machine_types=machine_type,
         account_id=username, account_ps=password):
    """start_crawling"""

    print hallcode, machine_types, account_id, account_ps
    gh = Ghost(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36", wait_timeout=100);
    loged = sign_in(gh, account_id, account_ps)
    if not loged[0]:
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

        goToMachines(gh, hallcode)
        button_index += 1
        js = """
        history.go(-1);
        """
        result, resources = gh.evaluate(js, expect_loading=True)

    gh.exit()
    print "ghost exits."

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
            if len(js_link) > 0:
                machine_range = hxs3.select('//td[5]/text()').extract()
                js_link = js_link[0]
                if "tableHistoryClick" in js_link:
                    if len(machine_range) > 0:
                        machine_range = machine_range[0]
                    else:
                        machine_range = ""
                    js_link = js_link.replace("javascript:", "")
                    print "executing:", js_link
                    result, resources = gh.evaluate(js_link, expect_loading=True)
                    getData(gh, hallcode, machine_range)
                    js = """
                    history.go(-1);
                    """
                    result, resources = gh.evaluate(js, expect_loading=True)
                    time.sleep(2)


if __name__=="__main__":
    start_crawling()
    
