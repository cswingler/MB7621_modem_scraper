import threading
import schedule
import time
import sys
from datetime import datetime, timedelta
from MB7621 import modem
import configparser

sampleConfigCfg = '''
[MB7621]
username=admin
password=admin
interval=15
'''
config = configparser.ConfigParser()
config.read('config.cfg')

try:
    u = config.get("MB7621", "username")
    p = config.get("MB7621", "password")
    i = int(config.get("MB7621", "interval"))
except configparser.NoOptionError:
    print("please define a config.cfg file and include username, password, and interval.")
    sys.exit()
except:
    print("unhandled configparser error %s" % sys.exc_info()[0])
    sys.exit()

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func, daemon=True)
    job_thread.start()
    print("%s threads: %s" %(datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),threading.active_count()) )
    
print('starting with interval: %i sec' % i)
with modem() as m:
    if m.login(u,p) == True:    
        m.getData()
        schedule.every(i).seconds.do(run_threaded,m.getData)
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print('Stopped.')
            if m.logout() == False:
                print("logout failed")
            sys.exit(0)
