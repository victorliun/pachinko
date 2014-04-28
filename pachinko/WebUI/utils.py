"""
utils module
"""
import json
from subprocess import call
from connectMongoCrawler import DBCrawlerConnection
def stop_cron():
    """
    stop cron job
    """
    call(['crontab', '-r'])
    print "crontab -r"

def start_cron():
    """
    start cron
    """
    call(['crontab', 'pachinko.cron'])
    print "crontab pachinko.cron"
    
def save_form(form_string):
    """save set crawler form data"""
    with open('crawler_last_setting.json', 'w+') as fi:
        fi.write(form_string)
    

def read_form():
    """Read string for crawler_last_setting.json."""
    with open('crawler_last_setting.json', 'r') as fi:
        form_string = fi.read()
    return form_string

def clean_form():
    """
    reset form data 
    """
    last_crawl = DBCrawlerConnection().getLatestCrawlerDetails()[0]
    form = {}
    form['username'] = last_crawl['username']
    form['password'] = last_crawl['password']
    form['signal'] = "STOP"
    form['target_hallcode'] = last_crawl['targetHallocde']
    form['target_machine_types'] = last_crawl['targetmachinetype']
    form['next_run_time'] = ''
    with open('crawler_last_setting.json', 'w+') as fi: 
        fi.write(json.dumps(form))
