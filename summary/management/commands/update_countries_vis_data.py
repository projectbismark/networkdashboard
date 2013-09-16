from networkdashboard.summary.geoip_helper import getLocation
import pygeoip
import psycopg2
import json
from networkdashboard.summary.models import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction, DatabaseError, IntegrityError

# def dump_all_latencies():
    # cursor = connection.cursor()
    
    # cursor.execute("DELETE FROM cv_rtt;")
    # try:
        # transaction.commit_unless_managed()
    # except DatabaseError, IntegrityError:
        # print "error deleting..."

    # servers = CVServers.objects.all()
    # for server in servers:
        # print "Retrieving records for server named ", server.name, " ..."
        # query =  "INSERT INTO cv_rtt \
                             # (country, server, day, ndevices, nmeasurements, latency) \
                             # SELECT \
                                 # d.country_code AS country, \
                                 # '" + server.ip.strip() + "', \
                                 # m_rtt.eventstamp::date AS day, \
                                 # count(distinct d.ip) AS ndevices, \
                                 # count(m_rtt.median) AS nmeasurements, \
                                 # avg(m_rtt.median) AS latency \
                             # FROM m_rtt \
                             # JOIN devicedetails AS d ON d.ip = m_rtt.srcip \
                             # WHERE m_rtt.dstip = '" + server.ip.strip() + "' GROUP BY d.country_code, day;"
        
        # cursor.execute(query)
        # try:
            # transaction.commit_unless_managed()
        # except DatabaseError, IntegrityError:
            # print "error inserting..."
			
def dump_all_latencies():
    cursor = connection.cursor()
    countries = Devicedetails.objects.values('country_code').distinct()
	count = 0
	t0 = datetime.now()
    for c in countries:
		params = []
		params.append(c)
        SQL =  "SELECT \
				m_rtt.eventstamp::date AS day, \
				count(distinct m_rtt.srcip) AS ndevices, \
				count(*) AS nmeasurements, \
				avg(m_rtt.average) AS latency \
				FROM m_rtt \
				JOIN devicedetails AS d ON d.ip = m_rtt.srcip \
				WHERE d.country_code=%s AND m_rtt.average>0 AND m_rtt.average<3000  \
				GROUP BY day;"
        cursor.execute(SQL,params)
		records = cursor.fetchall()
		for r in records:
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			count = r['nmeasurements']
			day = r['day']
			line = str(eventstamp) + ',' + str(avg) + ',' + str(count) + 'n' + day + '\n'
			f.write(line)
		f.close()
		count += 1
		t1 = datetime.now()
		print t1-t0
		print str(len(devices)-count) + " remaining"
	cursor.close()
			

def set_geoip_countries():
    devices = Devicedetails.objects.all()
    conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" + \
        settings.MGMT_PASS + "'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    for d in devices:
        id = "OW" + d.deviceid.upper().replace(":","")
        cursor.execute("select ip from devices where id='" + id + "'")
        iprow = (cursor.fetchone())
        if iprow is not None:
            d.ip = iprow[0]
            if len(d.ip)>0:
                gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
                country = gi.record_by_addr(d.ip)
                if country is not None:
                    d.country_code = country['country_code']
            d.save()

class Command(BaseCommand):
    def handle(self, *args, **options):
        set_geoip_countries()
        json_file = open(settings.PROJECT_ROOT + 'summary/countries_vis_dump/server_list.json')
        server_list = json.load(json_file)
        gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
        for server in server_list:
            loc = getLocation(server[0],gi)
            s = CVServers(ip=server[0])
            s.name = server[1]
            s.lat = loc['latitude']
            s.lon = loc['longitude']
            s.save()
        dump_all_latencies()
