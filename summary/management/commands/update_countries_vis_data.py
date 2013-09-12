from networkdashboard.summary.geoip_helper import getLocation
import pygeoip
import psycopg2
import json
from networkdashboard.summary.models import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction, DatabaseError, IntegrityError

def dump_all_latencies():
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM cv_rtt;")
    try:
        transaction.commit_unless_managed()
    except DatabaseError, IntegrityError:
        print "error deleting..."

    servers = CVServers.objects.all()
    for server in servers:
        print "Retrieving records for server named ", server.name, " ..."
        query =  "INSERT INTO cv_rtt \
                             (country, server, day, ndevices, nmeasurements, latency) \
                             SELECT \
                                 d.country_code AS country, \
                                 '" + server.ip.strip() + "', \
                                 m_rtt.eventstamp::date AS day, \
                                 count(distinct d.ip) AS ndevices, \
                                 count(m_rtt.median) AS nmeasurements, \
                                 avg(m_rtt.median) AS latency \
                             FROM m_rtt \
                             JOIN devicedetails AS d ON d.ip = m_rtt.srcip \
                             WHERE m_rtt.dstip = '" + server.ip.strip() + "' GROUP BY d.country_code, day;"
        
        cursor.execute(query)
        try:
            transaction.commit_unless_managed()
        except DatabaseError, IntegrityError:
            print "error inserting..."

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
        print "Setting IP and country fields for all devices in devicedetails..."
        set_geoip_countries()

        print "done\n\nPutting server data into database..."
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

        print "done\n\nSetting all latencies with dates...\n"
        dump_all_latencies()
