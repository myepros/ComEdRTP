import sys
import urllib
from datetime import datetime, timedelta
import time
import xively
import subprocess
import requests
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('config.ini')



FEED_ID = parser.get("xively", "FEED_ID")
API_KEY = parser.get("xively", "API_KEY")

# initialize api client
api = xively.XivelyAPIClient(API_KEY)

feed = api.feeds.get(FEED_ID)
 
lastRateTime = datetime.now() - timedelta(hours=1)
offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone

# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed):
    try:
        datastream = feed.datastreams.get("rate")
        return datastream
    except:
        datastream = feed.datastreams.create("rate", tags="Rate")
        return datastream

def getCurrentRate(datastream):
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
        dt = datetime(int(tv[0]), int(tv[1])+1, int(tv[2]), int(tv[3]), int(tv[4]), int(tv[5])) + timedelta(seconds=offset)
        if int(lastRateTime.strftime('%s')) < int(dt.strftime('%s')):
            ep = (dt - datetime(1970,1,1)).total_seconds() + offset
            data = data.replace("]", "")
            rate = float(data[data.find(')')+2:])
            datastream.current_value = rate
            datastream.at = dt

            try:
                datastream.update()
            except requests.HTTPError as e:
                print "HTTPError({0}): {1}".format(e.errno, e.strerror)

            print dt.isoformat(' ') + " Rate: " + str(rate) + " Epoc: " + str(ep)
            lastRateTime = dt

if __name__ == "__main__":
    lastRateTime = datetime.now() - timedelta(hours=1)
    datastream = get_datastream(feed)
    datastream.max_value = None
    datastream.min_value = None

    try:
        while 1:
            getCurrentRate(datastream)
            time.sleep(60*2)
    except KeyboardInterrupt:
        sys.exit(0)
