"""
utils module
"""
import json

def stop_crawling():
    """
    stop cron job
    """
    pass

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
    form = {}
    form['username'] = ''
    form['password'] = ''
    form['sigal'] = "STOP"
    form['target_hall'] = ''
    form['target_machine_types'] = ''
    with open('crawler_last_setting.json', 'w+') as fi: 
        fi.write(json.dumps(form))