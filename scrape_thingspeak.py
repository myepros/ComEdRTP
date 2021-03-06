import sys
import urllib
from datetime import datetime, timedelta
import time
import urllib2
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('config.ini')

API_KEY = parser.get("thingspeak", "API_KEY")

baseURL = 'https://api.thingspeak.com/update?api_key=' + API_KEY

offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone

def getCurrentRate():
    global lastRateTime
    rate = -100
    try:
        sock = urllib.urlopen("https://rrtp.comed.com/rrtp/ServletFeed?type=pricechartfiveminute")
        rtpdata = sock.read()
        sock.close()
    except:
        print "Error opening socket to rrtp.comed.com"
        return

    rtpdata = rtpdata.split('~', 1)[0]
    #print rtpdata
    rtpdata = rtpdata.split("], ")

    for data in rtpdata:
        timestr = data[data.find('(') + 1:data.find(')')]
        if len(timestr) < 4:
            continue
        tv = timestr.split(',')
        dt = datetime(int(tv[0]), int(tv[1])+1, int(tv[2]), int(tv[3]), int(tv[4]), int(tv[5]))
        if int(lastRateTime.strftime('%s')) < int(dt.strftime('%s')):
            data = data.replace("]", "")
            rate = float(data[data.find(')')+2:])
            try:
                f = urllib2.urlopen(baseURL + "&field1=%s" % (rate))
                print f.read()
                f.close()
            except:
                print "Error updating thingspeak."

            print dt.isoformat(' ') + " Rate: " + str(rate)
            lastRateTime = dt

if __name__ == "__main__":
    lastRateTime = datetime.now() - timedelta(minutes=1)

    try:
        while 1:
            getCurrentRate()
            time.sleep(60)
    except KeyboardInterrupt:
        sys.exit(0)
