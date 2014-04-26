"""
utils module
"""
import time

def sign_in(gh, account_id, account_ps):
    """
    Check yahoo account name and password if it is correct
    """
    page, resources = gh.open("http://fe.site777.tv/data/yahoo/login.php")
    gh.wait_for_selector('input[name=login]')
    print page.url 
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

def stop_crawling():
    """
    stop cron job
    """
    pass