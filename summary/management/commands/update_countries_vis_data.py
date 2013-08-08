from networkdashboard.summary.geoip_helper import getLocation
import pygeoip
import psycopg2
import json
from networkdashboard.summary.models import *
from django.conf import settings
from time import gmtime, strftime

def get_dict_cursor():
    conn_string = "host='" + settings.DATABASES['default']['HOST'] + \
                   "' dbname='" + settings.DATABASES['default']['NAME'] + \
                   "' user='" + settings.DATABASES['default']['USER'] + \
                   "' password='" + settings.DATABASES['default']['PASSWORD'] + "'";
                   
    conn = psycopg2.connect(conn_string)
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def dump_all_latencies(server):
    cursor = get_dict_cursor();

    cursor.execute("SELECT \
                        d.geoip_country AS country, \
                        count(distinct d.ip) AS ndevices, \
                        avg(m_rtt.average) AS avg_latency \
                    FROM m_rtt \
                    JOIN devicedetails AS d ON d.ip = m_rtt.srcip \
                    WHERE m_rtt.dstip = '" + server + "' GROUP BY d.geoip_country;"
                    );
                    
    records = cursor.fetchall();
    result = {}
    result['server'] = {}
    result['mapdata'] = {}

    gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
    loc = getLocation(server,gi)
    result['server']['lat'] = str(loc['latitude'])
    result['server']['lon'] = str(loc['longitude'])
    
    for row in records:
        result['mapdata'][row['country'].strip()] = [ row['avg_latency'], row['ndevices'] ]

    result['eventstamp'] = strftime("%Y/%m/%d", gmtime())

    file = open(settings.PROJECT_ROOT + 'summary/countries_vis_dump/' + server, "w")
    file.write(json.dumps(result));

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
                    d.geoip_country = country['country_code']

            d.save()

print "Setting IP and country fields for all devices in devicedetails..."
set_geoip_countries()

json_file = open(settings.PROJECT_ROOT + 'summary/countries_vis_dump/server_list.json')
server_list = json.load(json_file);
for server in server_list:
    print "Setting latentcies for server named ", server[1], "..."
    dump_all_latencies(server[0])
