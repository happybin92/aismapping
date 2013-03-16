import datetime
import os
import re
from django.http import HttpResponse
from django.shortcuts import render_to_response
import ais
import collections
import sqlite3


def home(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    resp = HttpResponse()
    return render_to_response("map.html")

def getVisibleShips(request):
    toprightx = request.GET.get('toprightx')
    toprighty = request.GET.get('toprighty')
    bottomleftx = request.GET.get('bottomleftx')
    bottomlefty = request.GET.get('bottomlefty')

    conn = sqlite3.connect(r"ais.db")
    resp = HttpResponse()
    with conn:

        cur = conn.cursor()
        cur.execute("SELECT * FROM AIVDM WHERE x > {0} AND x < {1} AND y > {2} ANd y < {3} LIMIT 20"
                    .format(bottomleftx, toprightx, bottomlefty, toprighty))
        rows = cur.fetchall()

        for row in rows:
            resp.write(row)

    return resp


def rawdata(request):
    resp = HttpResponse()
    mmsis = []
    aiss = []

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"nmea-sample.txt"),'r') as f:
        for line in f:
            m = re.search('!AIVDM,[\w]?,[\w]?,[\w]?,[\w]?,(?P<ais>[^,]*)', line)
            if m:
                aisData = m.group('ais')
                try:
                    aiss.append(ais.decode(aisData,0))
                    mmsis.append(ais.decode(aisData,0).get('mmsi'))
                except:
                    pass
                    #resp.write("Could not decode " + aisData)
        resp.write("<br/>")
        repeated = ([x for x, y in collections.Counter(mmsis).items() if y > 2])
        for mm in repeated:
            for rm in (item for item in aiss if item["mmsi"] == mm):
                resp.write(str(rm.get('mmsi')) + " at " + str(rm.get('timestamp')) + " at " + str(rm.get('x')) + "," + str(rm.get('y')))
                resp.write("<br/>")

    #resp.write(file(os.path.join(os.path.dirname(os.path.abspath(__file__)),"nmea-sample.txt")).read())
    return resp


def storedata(request):

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

    return HttpResponse("Done")
