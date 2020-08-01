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
except configparser.NoOptionError:
    print("please define a config.cfg file and include username, password, and interval.")
    sys.exit()
except:
    print("unhandled configparser error %s" % sys.exc_info()[0])
    sys.exit()


with modem() as m:
    if m.login(u,p) == True:    
        r = m.getMotoSecurity_RebootModem()
        print("reboot %s" % r)