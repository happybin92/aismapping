import datetime
import os
import re
from django.http import HttpResponse
from django.shortcuts import render_to_response
import ais
import collections


def home(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    resp = HttpResponse()
    return render_to_response("map.html")
    #resp.write(ais.decode('15PIIv7P00D5i9HNn2Q3G?wB0t0I', 0))
    #return resp

def rawdata(request):
    resp = HttpResponse()
    mmsis = []
    aiss = []

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"nmea-sample.txt"),'r') as f:
        for line in f:
            m = re.search('!AIVDM,[\w]?,[\w]?,[\w]?,[\w]?,(?P<ais>[^,]*)', line)
            if m:
                aisData = m.group('ais')
                #resp.write("<br /><br />")
                try:
                    aiss.append(ais.decode(aisData,0))
                    mmsis.append(ais.decode(aisData,0).get('mmsi'))
                except:
                    pass
                    #resp.write("Could not decode " + aisData)

        #resp.write("Total: " + str(len(mmsis)))
        resp.write("<br/>")
        repeated = ([x for x, y in collections.Counter(mmsis).items() if y > 2])
        for mm in repeated:
            for rm in (item for item in aiss if item["mmsi"] == mm):
                resp.write(str(rm.get('mmsi')) + " at " + str(rm.get('timestamp')) + " at " + str(rm.get('x')) + "," + str(rm.get('y')))
                resp.write("<br/>")
            #resp.write(repeatingMmsi.get('mmsi'))
            #resp.write(mm)


    #resp.write(file(os.path.join(os.path.dirname(os.path.abspath(__file__)),"nmea-sample.txt")).read())
    return resp

    #return render_to_response("map.html")


def storedata(request):
    import sqlite3
    conn = sqlite3.connect(r"ais.db")

    with conn:

        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS AIVDM")
        cur.execute("CREATE TABLE IF NOT EXISTS AIVDM(mmsi INT, x DEC, y DEC, nav_status INT, true_heading INT, timestamp INT)")

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"nmea-sample.txt"),'r') as f:
            for line in f:
                m = re.search('!AIVDM,[\w]?,[\w]?,[\w]?,[\w]?,(?P<ais>[^,]*)', line)
                if m:
                    aisData = m.group('ais')
                    #resp.write("<br /><br />")
                    try:
                        aisDecoded = ais.decode(aisData,0)

                        if aisDecoded:
                            if aisDecoded.get('mmsi') <= 0 or aisDecoded.get('x') > 180 or aisDecoded.get('y') > 90:
                                continue

                            cur.execute("INSERT INTO AIVDM VALUES(" + str(aisDecoded.get('mmsi')) + ","
                                        + str(aisDecoded.get('x')) + "," + str(aisDecoded.get('y')) + ","
                                        + str(aisDecoded.get('nav_status')) + "," + str(aisDecoded.get('true_heading')) + ","
                                        + str(aisDecoded.get('timestamp'))
                                        + ");")
                    except Exception as e:
                        print e.message

            #repeated = ([x for x, y in collections.Counter(mmsis).items() if y > 2])
            #for mm in repeated:
            #    for rm in (item for item in aiss if item["mmsi"] == mm):
                    #resp.write(str(rm.get('mmsi')) + " at " + str(rm.get('timestamp')) + " at " + str(rm.get('x')) + "," + str(rm.get('y')))
                    #resp.write("<br/>")
                #resp.write(repeatingMmsi.get('mmsi'))
                #resp.write(mm)


        #resp.write(file(os.path.join(os.path.dirname(os.path.abspath(__file__)),"nmea-sample.txt")).read())

    return HttpResponse("Done")
