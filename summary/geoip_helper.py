from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from django.conf import settings
from networkdashboard.summary.models import *
import cvs_helper,datetime_helper, views_helper
import isp_mappings
import pygeoip
import psycopg2
from django.core.cache import cache
import random

def get_coordinates_for_googlemaps():
	coordstring = ""
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	distinct = getIPList()
	deviceIDList = getDeviceIDList()
	deviceIDs = list()
	for ID in deviceIDList:
		deviceIDs.append(ID[0])
	data_type="coord"
	devtype = 'address'
	i = 0
	for row in distinct:
		loc = getLocation(row[0],gi)
		lat = str(loc['latitude'])
		lon = str(loc['longitude'])
		hashdevice = views_helper.get_hash(deviceIDs[i][2:])
		i += 1
		coordstring += devtype
		coordstring += ":"
		coordstring += data_type
		coordstring += ":"
		coordstring += lat
		coordstring += ":"
		coordstring += lon
		coordstring += ":"
		coordstring += hashdevice
		coordstring += "\n"

	distinct_ips = IpResolver.objects.all()
	data_type="coord"
	for row_ip in distinct_ips:
		lat = str(row_ip.latitude)
		lon = str(row_ip.longitude)
		devtype = str(row_ip.type)
		hashdevice = views_helper.get_hash(deviceIDs[0]) # '0' is temp. replace '0'.
		coordstring += devtype
		coordstring += ":"
		coordstring += data_type
		coordstring += ":"
		coordstring += lat
		coordstring += ":"
		coordstring += lon
		coordstring += ":"
		coordstring += hashdevice
		coordstring += "\n"

	return HttpResponse(coordstring)
	
# def get_coordinates_for_googlemaps():
	# coord_data = []
	# gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	# device_ips = getIPList()
	# servers = IpResolver.objects.all()
	# dev_type = "device"
	# for row in device_ips:
		# value={}
		# loc = getLocation(row[0],gi)
		# lat = str(loc['latitude'])
		# lon = str(loc['longitude'])
		# device = get_devices_by_ip(row[0])
		# hash = DeviceDetails.objects.filter(deviceid = device)[0]['hashkey']
		# value['dev_type'] = dev_type
		# value['lat'] = lat
		# value['lon'] = lon
		# value['hash'] = hash
		# coord_data.append(value)
	# dev_type = "server"
	# for row_ip in servers:
		# value = {}
		# lat = str(row_ip.latitude)
		# lon = str(row_ip.longitude)
		# device = get_devices_by_ip(row_ip.ip)
		# hash = DeviceDetails.objects.filter(deviceid = device)[0]['hashkey']
		# value['dev_type'] = dev_type
		# value['lat'] = lat
		# value['lon'] = lon
		# value['hash'] = hash
		# coord_data.append(value)
	# return HttpResponse(coordstring)

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
	
def get_device_count():
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select COUNT(*) from devices")
	count = cursor.fetchone()
	#print records
	print count[0]
	return count[0]

def getDeviceIDList():
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select id from devices")
	records = cursor.fetchall()
	#print records
	return records
	
def get_ip_by_device(device):
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select ip from devices where SUBSTRING(id,3)='" + device.upper() +"'")
	records = cursor.fetchall()[0]
	return records
	
def get_provider_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	isp = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
	for m in mappings:
		if(isp.lower().find(m[0].lower())!=-1):
			isp = m[1]		
	return isp
	
def get_ips_by_provider(isp):
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	ret = []
	ip_list = getIPList()
	for ip in ip_list:
		try:
			name = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
			for m in mappings:
				if(name.lower().find(m[0].lower())!=-1):
					name = m[1]
					break
			if (name==isp):	
				ret.append(ip[0])
		except:
			continue
	return ret
	
def get_ips_by_city(city):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	ret = []
	ip_list = getIPList()
	for ip in ip_list:
		try:
			record = gi.record_by_addr(ip[0])
			if (record==city):	
				ret.append(ip[0])
		except:
			continue
	return ret
	
def get_devices_by_ips(ips):
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	ret = []
	for ip in ips:
		cursor.execute("select SUBSTRING(id,3) from devices where ip='" + ip +"'")
		record = cursor.fetchall()[0][0].lower()
		ret.append(record)
	return ret
	
def get_devices_by_ip(ip):
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select SUBSTRING(id,3) from devices where ip='" + ip +"'")
	records = cursor.fetchall()[0]
	return records
	
def get_country_count():
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	country_list = []
	ip_list = getIPList()
	for ip in ip_list:
		new_country = True
		try:
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
		except:
			continue
	return country_list
	
def get_city_count():
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	city_list = []
	ip_list = getIPList()
	for ip in ip_list:
		new_city = True
		try:
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
		except:
			continue		
	return city_list
	
def get_provider_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	isp = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
	for m in mappings:
		if(isp.lower().find(m[0].lower())!=-1):
			isp = m[1]		
	return isp
	
def get_city_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	return gi.record_by_addr(ip[0])
	
def get_isp_count():
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	isp_list = []
	ip_list = getIPList()
	for ip in ip_list:
		new_isp = True
		
		try:
			name = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
			for m in mappings:
				if(name.lower().find(m[0].lower())!=-1):
					name = m[1]
					break
			for isp in isp_list:
				if isp['isp']==name:
					isp['count']+=1
					new_isp = False
			if ((new_isp) and (name!='')):
				value = {}
				value['isp']=name
				value['count']=1
				isp_list.append(value)
		except:
			continue
	return isp_list