import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import time
import sys
from datetime import datetime, timedelta


class modem():
    """A modem scrapper class for MB7621"""
    
    username="admin"
    password="admin"

    session_status = False
        
    url_login           = 'http://192.168.100.1/login.asp'
    url_login_post      = 'http://192.168.100.1/goform/login'
    url_home            = 'http://192.168.100.1/MotoHome.asp'
    url_swinfo          = "http://192.168.100.1/MotoSwInfo.asp"
    url_conn            = "http://192.168.100.1/MotoConnection.asp"
    url_log             = "http://192.168.100.1/MotoSnmpLog.asp"
    url_logout          = 'http://192.168.100.1/logout.asp'
    url_security        = 'http://192.168.100.1/MotoSecurity.asp'
    url_securiy_post    = 'http://192.168.100.1/goform/MotoSecurity'

    payload_login = {
        'loginUsername': 'admin',
        'loginPassword': 'admin'
    }
    
    # 1 is defined as reboot for my modem. 
    # Verify this is correct for your version of modem firmware before using
    # sending the wrong value could reset your modem to factory defaults
    reboot_payload = {
        'MotoSecurityAction': '1'
    }

    def __init__(self): 
        self.s = requests.Session()
        self.engine = create_engine('sqlite:///MB7621.db', echo=False)
        return

    
    def __enter__(self):
        return self

    
    def __exit__(self, exc_type, exc_value, traceback):
        return

    
    def login(self,username,password):
        self.username = username
        self.password = password
        self.payload_login["loginUsername"] = self.username
        self.payload_login["loginPassword"] = self.password
        login_page = self.s.get(self.url_login)
        resp = self.s.post(self.url_login_post, data=self.payload_login)
        if 'Login is temporarily disabled for 5 minutes because of too many failed attempts' in resp.text: 
            print("Hit the DoS limiter, sleeping 5 minutes.")
            time.sleep(5*60)
        if resp.ok == False:
            self.session_status = False
        else:
            print("---Login text---")
            print(resp.text)
            self.session_status = True
        return self.session_status
 

    def logout(self):
        if self.session_status == True:
            resp = self.s.get(self.url_logout)
            self.s.close()
            self.session_status = False
        return resp.ok 


    def show(self):
        print("login user: %s pass: %s" % (self.username,self.password) )
        print(self.login_payload)


    def getMotoSecurity_RebootModem(self):
        if self.session_status == True:
            r = requests.get(self.url_security)
            r = requests.post(self.url_securiy_post, data=self.reboot_payload)
            return r
        else:
            return {'getMotoSecurity_RebootModem':False}


    def getMotoHome(self,timestamp):
        if self.session_status == True:
            r = requests.get(self.url_home)
            soup = BeautifulSoup(r.text, 'html.parser')
            # Periodically, there's no table because we need to test ofr 
            # <title>Motorola Cable Modem : Login</title>
            # (showing a failed login)
            if 'Login' in soup.find('title').text: 
                print(f"uh oh, login probably failed, got a title of \"{soup.find('title').text}\"")
            tr = soup.find_all('tr')
            online = tr[5].find('td',class_="moto-param-value").text
            downstream = tr[7].find('td',class_="moto-param-value").text
            upstream = tr[8].find('td',class_="moto-param-value").text
            mac = tr[12].find('td',class_="moto-param-value").text
            softwareVersion = tr[13].find('td',class_="moto-param-value").text
            return [{
                "timestamp":timestamp,
                'OnlineStatus':online,
                'Downstream':downstream,
                'Upstream':upstream,
                'MAC':mac,
                'SoftwareVersion':softwareVersion
            }]
        else:
            return {'getMotoHome':False}

        
    def getMotoSwInfo(self,timestamp):
        if self.session_status == True:
            r = requests.get(self.url_swinfo)
            soup = BeautifulSoup(r.text, 'html.parser')
            tr = soup.find_all('td',class_="moto-content-value")
            cableSpecVersion = tr[0].text
            hardwareVersion = tr[1].text
            softwareVersion = tr[2].text
            cableModemMacAddr = tr[3].text
            cableModemSerialNum = tr[4].text
            CmCert = tr[5].text
            CmCertValue = tr[6].text
            return [{
                "timestamp":timestamp,
                "DOCSIS":cableSpecVersion,
                "HardwareVersion":hardwareVersion,
                "SoftwareVersion":softwareVersion,
                "ModemMAC":cableModemMacAddr,
                "ModemSerial":cableModemSerialNum,
                "CMCertStatus":CmCert,
                "CMCertValue":CmCertValue
            }]
        else:
            return {'getMotoSwInfo':False}

        
    def getMotoConnection(self,timestamp):
        if self.session_status == True:
            r = requests.get(self.url_conn)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find_all('table',class_="moto-table-content")
            # basic
            acqDownstreamChannel_freq = table[1].find_all('tr')[1].find_all('td',class_="moto-content-value")[0].text            
            acqDownstreamChannel_status = table[1].find_all('tr')[1].find_all('td',class_="moto-content-value")[1].text            
            upstreamConnection_status1 = table[1].find_all('tr')[2].find_all('td',class_="moto-content-value")[0].text
            upstreamConnection_status2 = table[1].find_all('tr')[2].find_all('td',class_="moto-content-value")[1].text
            bootState_status1 = table[1].find_all('tr')[3].find_all('td',class_="moto-content-value")[0].text
            bootState_status2 = table[1].find_all('tr')[3].find_all('td',class_="moto-content-value")[1].text
            configFile_status1 = table[1].find_all('tr')[4].find_all('td',class_="moto-content-value")[0].text
            configFile_status2 = table[1].find_all('tr')[4].find_all('td',class_="moto-content-value")[1].text
            security_status1 = table[1].find_all('tr')[5].find_all('td',class_="moto-content-value")[0].text
            security_status2 = table[1].find_all('tr')[5].find_all('td',class_="moto-content-value")[1].text
            systemUpTime = table[2].find_all('tr')[0].find_all('td',class_="moto-content-value")[0].text
            networkAccess = table[2].find_all('tr')[1].find_all('td',class_="moto-content-value")[0].text
            basic = [{
                'timestamp':timestamp,
                'downFreq':acqDownstreamChannel_freq,
                'downStatus':acqDownstreamChannel_status,
                'upStatus1':upstreamConnection_status1,
                'upStatus2':upstreamConnection_status2,
                'bootStatus1':bootState_status1,
                'bootStatus2':bootState_status2,
                'configStatus1':configFile_status1,
                'configStatus2':configFile_status2,
                'securityStatus1':security_status1,
                'securityStatus2':security_status2,
                'systemUpTime':systemUpTime,
                'networkAccess':networkAccess
            }]
            # downstream
            iterele = iter(table[3].find_all('tr'))
            next(iterele)
            down = []
            down_columns=['timestamp','Channel','Locked','Modulation','Channel ID','Freq_MHz','Pwr_dBmV','SNR_dB','Corrected','Uncorrected']
            for x in iterele:
                down_data=[timestamp]
                if x.find_all('td',class_="moto-content-value")[0].text != "Total":
                    for y in range(9):
                        z = x.find_all('td',class_="moto-content-value")[y].text
                        down_data.append(z)
                    down_dict = dict(zip(down_columns,down_data))
                    down.append(down_dict)

            # upstream
            iterele = iter(table[4].find_all('tr'))
            next(iterele)
            up = []
            up_columns=['timestamp','Channel','Locked','ChannelType','ChannelId','SymbRate_ksym_per_s','Freq_MHz','Pwr_dBmV']
            for x in iterele:
                up_data=[timestamp]
                for y in range(7):
                    z = x.find_all('td',class_="moto-content-value")[y].text
                    up_data.append(z)
                up_dict = dict(zip(up_columns,up_data))
                up.append( up_dict )
            return basic,down,up

        else:
            return {'getMotoConnection':False}

        
    # TODO
    # keep track of elements from the dataframe that are already inserted into the db
    # only insert new elements like ones event times greater than last inserted eventtime
    def getMotoSnmpLog(self,timestamp):
        if self.session_status == True:
            r = requests.get(self.url_log)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find_all('table',class_="moto-table-content")
            # skip the first element which is the header
            iterele = iter(table[0].find_all('tr'))
            next(iterele)
            log_columns=['timestamp','time','level','message']
            log = []
            for x in iterele:
                y = x.find_all('td',class_="moto-param-value")
                # skip entries that return no data
                if len(y) == 3:
                    # skip entries with empty string data
                    if len(y[0].text.strip()) > 0:
                        log_data = [timestamp,y[0].text.strip(),y[1].text.strip(),y[2].text.strip()]
                        log_dict = dict(zip(log_columns,log_data))
                        log.append(log_dict)
            return log

        else:
            return {'getMotoSnmpLog':False}
    
    
    def getData(self):

        timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

        df_home = pd.DataFrame(self.getMotoHome(timestamp))
        df_home.to_sql(name='home', con=self.engine, if_exists='append')

        df_sw = pd.DataFrame(self.getMotoSwInfo(timestamp))
        df_sw.to_sql('sw', con=self.engine, if_exists='append')

        basic,down,up = self.getMotoConnection(timestamp)
        df_basic = pd.DataFrame(basic)
        df_basic.to_sql('conn_basic', con=self.engine, if_exists='append')

        df_up = pd.DataFrame(up)
        df_up = df_up.set_index('Channel')
        df_up.to_sql('conn_up', con=self.engine, if_exists='append')

        df_down = pd.DataFrame(down)
        df_down = df_down.set_index('Channel')
        df_down.to_sql('conn_down', con=self.engine, if_exists='append')

        log = self.getMotoSnmpLog(timestamp)
        df_log = pd.DataFrame(log)
        df_log.tail(3).to_sql('log', con=self.engine, if_exists='append')


#********************************************
if __name__ == "__main__":
    import threading
    import schedule
    import time
    from datetime import datetime, timedelta
    import sys
    from MB7621 import modem

    interval = 15   # seconds
 
    def run_threaded(job_func):
        job_thread = threading.Thread(target=job_func, daemon=True)
        job_thread.start()
        print("%s threads: %s" %(datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),threading.active_count()) )
        
    print('starting with interval: %i sec' % interval)
    with modem() as m:
        if m.login("admin","TTBkdWx1NQ==") == True:    
            m.getData()
            schedule.every(interval).seconds.do(run_threaded,m.getData)
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            except KeyboardInterrupt:
                print('Stopped.')
                if m.logout() == False:
                    print("logout failed")
                sys.exit(0)


