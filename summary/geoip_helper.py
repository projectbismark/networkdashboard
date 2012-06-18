from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
import cvs_helper,datetime_helper,views_helper
import pygeoip
import psycopg2
import geoip_values
from django.core.cache import cache
import random

def get_coordinates_for_googlemaps():
	coordstring = ""
	gi = pygeoip.GeoIP(geoip_values.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
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
	conn_string = "host='localhost' dbname='" + geoip_values.MGMT_DB + "' user='"+ geoip_values.MGMT_USERNAME  +"' password='" +  geoip_values.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select ip from devices")
	records = cursor.fetchall()
	#print records
	return records
	
	
def get_country_count():
	gi = pygeoip.GeoIP(geoip_values.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	country_list = []
	ip_list = getIPList()
	for ip in ip_list:
		new_country = True
		name = gi.country_name_by_addr(ip[0])
		for c in country_list:
			if c['country']==name:
				c['count']+=1
				new_country = False
		if new_country:
			value = {}
			value['country']=name
			value['count']=1
			country_list.append(value)
	return country_list
	
def get_city_count():
	gi = pygeoip.GeoIP(geoip_values.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	city_list = []
	ip_list = getIPList()
	for ip in ip_list:
		new_city = True
		rec = gi.record_by_addr(ip[0])
		for c in city_list:
			if ((c['city']==rec['city'])and(c['region']==rec['region_name'])):
				c['count']+=1
				new_city = False
		if ((new_city) and (rec['city']!='')):
			value = {}
			value['city']=rec['city']
			value['region']=rec['region_name']
			value['country']=rec['country_name']
			value['count']=1
			city_list.append(value)
			
	return city_list
	
def get_isp_count():
	gi = pygeoip.GeoIP(geoip_values.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	isp_list = []
	ip_list = getIPList()
	for ip in ip_list:
		new_isp = True
		name = gi.org_by_addr(ip[0])
		for isp in isp_list:
			if isp['isp']==name:
				isp['count']+=1
				new_isp = False
		if ((new_isp) and (name!='')):
			value = {}
			value['isp']=name
			value['count']=1
			isp_list.append(value)
			
	return isp_list