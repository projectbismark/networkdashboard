from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
import cvs_helper,datetime_helper,views_helper
import pygeoip
import psycopg2
from django.conf import settings
from django.core.cache import cache
import random

def get_coordinates_for_googlemaps():
	coordstring = ""
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	distinct = getIPList()
	data_type="coord"
	devtype = 'address'
	i=0
	for row in distinct:
		loc = getLocation(row[0],gi)
		lat = str(loc['latitude'])
		lon = str(loc['longitude'])

		coordstring += devtype
		coordstring += ":"
		coordstring += data_type
		coordstring += ":"
		coordstring += lat
		coordstring += ":"
		coordstring += lon
		coordstring += "\n"
		i+=1
		
	distinct_ips = IpResolver.objects.all()
	data_type="coord"
	for row_ip in distinct_ips:

		lat = str(row_ip.latitude)
		lon = str(row_ip.longitude)
		devtype = str(row_ip.type)
		coordstring += devtype
		coordstring += ":"
		coordstring += data_type
		coordstring += ":"
		coordstring += lat
		coordstring += ":"
		coordstring += lon
		coordstring += "\n"

	return HttpResponse(coordstring)


def getLocation(ip,gi):
	
	ret = cache.get(ip)
	
	if(ret != None):
		return ret
	
	gi_rec = gi.record_by_addr(ip)
	
	cache.set(ip,gi_rec,random.randint(1000, 10000))
	
	return gi_rec

def getIPList():
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select ip from devices")
	records = cursor.fetchall()
	#print records
	return records
	
