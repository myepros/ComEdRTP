import sys
import urllib
from datetime import datetime, timedelta
import time
from ISStreamer.Streamer import Streamer
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('config.ini')

ACCESS_KEY = parser.get("initialstate", "ACCESS_KEY")

streamer = Streamer(bucket_name="ComEd RTP", access_key=ACCESS_KEY)
lastRateTime = datetime.now() - timedelta(hours=1)
offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone

def getCurrentRate():
    global lastRateTime
    rate = -100
    sock = urllib.urlopen("https://rrtp.comed.com/rrtp/ServletFeed?type=pricechartfiveminute")
    rtpdata = sock.read()
    sock.close()

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
            ep = (dt - datetime(1970,1,1)).total_seconds() + offset
            data = data.replace("]", "")
            rate = float(data[data.find(')')+2:])
            streamer.log("Rate", rate, ep)
            print dt.isoformat(' ') + " Rate: " + str(rate) + " Epoc: " + str(ep)
            lastRateTime = dt
        streamer.flush()

if __name__ == "__main__":
    lastRateTime = datetime.now() - timedelta(hours=1)
    try:
        while 1:
            getCurrentRate()
            time.sleep(60*2)
    except KeyboardInterrupt:
        sys.exit(0)
