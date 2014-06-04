"""
utils module
"""
import json
import itertools
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


BALL_SPIN_COST = -15
SPIN_AVERAGE = -0.017
BALL_PURCHASE = 4
BALL_CASHOUT = 3.57
BALL_JACKPOT = 1870
FREE_SPINS = 100

def add_cash_payout(lst):
    """
    This function aim to add cash payout to the exist list. 
    Five new colunms will add into the list.
    They are Cash+/-, Ball+/-, Ball win to this point, Cash out at this point, 
    and Cash result
    """
    for value, group in itertools.groupby(lst, lambda x:x['date']):
        update_cash_payout(list(group))
    return lst

def update_cash_payout(group):
    result = []
    total_cashout = 0
    for index, item in enumerate(group):
        spin = item['spin_count_of_win']
        if index == 0:
            if item['renchan'] == 0:
                item['cash'] = int(round(spin / SPIN_AVERAGE)) 
                ball_puchased = int(round(item['cash'] / 1000.0 * 250 ))
                item['balls_won'] = BALL_JACKPOT
                item['balls'] = ball_puchased + item['balls_won']
                if item['balls'] > 0:
                    item['balls'] = 0
                total_cashout += item['cash']
                item['cashout'] = int(round(item['balls_won'] *  BALL_CASHOUT))
                item['cash_result'] = item['cash'] + item['cashout']
            else:
                # renchan no cost for spin
                item['cash'] = 0 
                item['balls_won'] = BALL_JACKPOT
                item['balls'] = 0
                item['cashout'] = int(round(item['balls_won'] *  BALL_CASHOUT))
                item['cash_result'] = total_cashout + item['cashout']
        elif index != len(group) - 1: # not the last one
            if item['renchan'] == 0:
                spin_balls = ( spin - FREE_SPINS ) * BALL_SPIN_COST
                ball_cost = spin_balls + group[index-1]['balls_won']
                if ball_cost > 0:
                    item['balls_won'] = BALL_JACKPOT + ball_cost
                    item['balls'] = 0
                    item['cash'] = group[index-1]['cash']
                else:
                    item['balls_won'] = BALL_JACKPOT
                    item['balls'] = spin_balls + group[index-1]['balls_won'] + item['balls_won'] 
                    item['cash'] = int(round(( spin - FREE_SPINS ) / SPIN_AVERAGE))
                    total_cashout += item['cash']
                item['cashout'] = int(round(item['balls_won'] * BALL_CASHOUT))
                item['cash_result'] = item['cashout'] + total_cashout
            else:# Renchan win, on cost of spin
                item['cash'] = group[index-1]['cash']
                item['balls_won'] = group[index -1]['balls_won'] + BALL_JACKPOT
                item['balls'] = 0
                item['cashout'] = int(round(item['balls_won'] *  BALL_CASHOUT))
                item['cash_result'] = item['cashout'] + total_cashout
        #finish
        if item['time_of_win'] == 'NaN' and item['win_number'] == '--':
            ## stop calculate
            item['balls'] = ( spin - FREE_SPINS ) * BALL_SPIN_COST
            item['cash'] = int(round(( spin - FREE_SPINS ) / SPIN_AVERAGE))
            item['cashout'] = 0
            item['balls_won'] = 0
            item['cash_result'] = total_cashout + item['cash']
        result.append(item)
    return result
