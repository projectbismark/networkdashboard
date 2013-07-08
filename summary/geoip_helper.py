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

# def get_coordinates_for_googlemaps():
	# coordstring = ""
	# gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	# distinct = getIPList()
	# deviceIDList = getDeviceIDList()
	# deviceIDs = list()
	# for ID in deviceIDList:
		# deviceIDs.append(ID[0])
	# data_type="coord"
	# devtype = "address"
	# i = 0
	# for row in distinct:
		# loc = getLocation(row[0],gi)
		# lat = str(loc['latitude'])
		# lon = str(loc['longitude'])
		# hashdevice = views_helper.get_hash(deviceIDs[i][2:])
		# i += 1
		# coordstring += devtype
		# coordstring += ":"
		# coordstring += data_type
		# coordstring += ":"
		# coordstring += lat
		# coordstring += ":"
		# coordstring += lon
		# coordstring += ":"
		# coordstring += hashdevice
		# coordstring += "\n"
	# distinct_ips = IpResolver.objects.all()
	# data_type="coord"
	# for row_ip in distinct_ips:
		# lat = str(row_ip.latitude)
		# lon = str(row_ip.longitude)
		# devtype = str(row_ip.type)
		# hashdevice = views_helper.get_hash(deviceIDs[0]) # '0' is temp. replace '0'.
		# coordstring += devtype
		# coordstring += ":"
		# coordstring += data_type
		# coordstring += ":"
		# coordstring += lat
		# coordstring += ":"
		# coordstring += lon
		# coordstring += ":"
		# coordstring += hashdevice
		# coordstring += "\n"

	# return HttpResponse(coordstring)
	
def get_coordinates_for_googlemaps():
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	coord_data = []
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	device_ips = getIPList()
	servers = IpResolver.objects.all()
	cached = JsonCache.objects.all()
	active_thresh = datetime_helper.get_daterange_start(7)
	for row in device_ips:
		try:
			value={}
			loc = getLocation(row[0],gi)
			lat = loc['latitude']
			lat = str(randomize_latitude(loc['latitude']))
			lon = str(loc['longitude'])
			cursor.execute("select SUBSTRING(id,3) from devices where ip='" + row[0] +"'")
			device = cursor.fetchone()
			hash = views_helper.get_hash(device[0])
			isp = get_provider_by_ip(row)
			value['isp'] = isp
			if hash=="":
				value['dev_type'] = "unregistered"
			else:
				d = format_mac_address(device[0])
				active_count = cached.filter(deviceid=d,eventstamp__gte=active_thresh).count()
				if active_count>0:
					value['dev_type'] = "active"
				else: 
					value['dev_type'] = "inactive"
			value['lat'] = lat
			value['lon'] = lon
			value['hash'] = hash
			coord_data.append(value)
		except:
			continue
	dev_type = "server"
	for row_ip in servers:
		try:
			value = {}
			loc = getLocation(row_ip.ip,gi)
			lat = str(row_ip.latitude)
			lon = str(row_ip.longitude)
			hash = ""
			value['dev_type'] = dev_type
			value['isp'] = ""
			value['lat'] = lat
			value['lon'] = lon
			value['hash'] = hash
			coord_data.append(value)
		except:
			continue
	return coord_data

def getLocation(ip,gi):
	ret = cache.get(ip)
	if(ret != None):
		return ret
	gi_rec = gi.record_by_addr(ip)
	cache.set(ip,gi_rec,random.randint(1000, 10000))
	return gi_rec

def getIPList():
	devices = Devicedetails.objects.values('deviceid').distinct()
	ips=[]
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	for d in devices:
		id = "OW" + d['deviceid'].upper().replace(":","")
		cursor.execute("select ip from devices where id='" + id + "'")
		ips.append(cursor.fetchone())
	return ips
	
def getIPListActive():
	active_thresh = datetime_helper.get_daterange_start(7)
	devices = JsonCache.objects.filter(eventstamp__gte=active_thresh).values('deviceid').distinct()
	ips=[]
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	for d in devices:
		id = "OW" + d['deviceid'].upper().replace(":","")
		cursor.execute("select ip from devices where id='" + id + "'")
		ips.append(cursor.fetchone())
	return ips
	
def format_mac_address(ip):
	return ':'.join(ip[i:i+2] for i in range(0, len(ip), 2)).lower()

def getMACList():
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select id from devices")
	records = cursor.fetchall()
	return records
	
def get_device_count():
	device_count = JsonCache.objects.values('deviceid').distinct().count()
	# conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	# conn = psycopg2.connect(conn_string)
	# cursor = conn.cursor()
	# cursor.execute("select COUNT(*) from devices")
	# count = cursor.fetchone()
	return device_count

def get_active_count():
	active_thresh = datetime_helper.get_daterange_start(7) 
	device_count = JsonCache.objects.filter(eventstamp__gte=active_thresh).values('deviceid').distinct().count()
	# conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	# conn = psycopg2.connect(conn_string)
	# cursor = conn.cursor()
	# cursor.execute("select COUNT(*) from devices")
	# count = cursor.fetchone()
	return device_count

def getDeviceIDList():
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select id from devices")
	records = cursor.fetchall()
	return records
	
def get_city_by_device(device):
	ip = get_ip_by_device(device)
	city = get_city_by_ip(ip)
	return city['city']
	
def get_country_by_city(city):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	ips = getIPList()
	for ip in ips:
		try:
			record = gi.record_by_addr(ip[0])
			if record['city']==city:
				return record['country_name']
		except:
			continue
	return ''
		
	
def get_country_by_device(device):
	ip = get_ip_by_device(device)
	country = get_city_by_ip(ip)
	return country['country_name']
	
	
def get_ip_by_device(device):
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select ip from devices where SUBSTRING(id,3)='" + device.upper() +"'")
	records = cursor.fetchall()
	if len(records)>0:
		return records[0]
	else:
		return ""
	
	
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
	
def get_ips_by_provider_and_country(isp,country):
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	gi2 = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	ret = []
	ip_list = getIPList()
	for ip in ip_list:
		try:
			name = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
			ip_country = gi2.record_by_addr(ip[0])['country_name']
			for m in mappings:
				if(name.lower().find(m[0].lower())!=-1):
					name = m[1]
					break
			if (((name==isp) and (ip_country==country)) or ((name==isp) and (country=="none"))):
				ret.append(ip[0])
		except:
			continue
	return ret
	
def get_diversified_ips_by_provider_and_country(isp,country):
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	gi2 = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	ret = []
	ip_list = getIPList()
	dist_level = 0
	country_list = []
	while True:
		new_device = False
		for ip in ip_list:
			try:
				country_count = 0
				new_ip = True
				for r in ret:
					if r==ip[0]:
						new_ip = False
						break
				if not new_ip:
					continue
				name = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
				ip_country = gi2.record_by_addr(ip[0])['country_name']
				for m in mappings:
					if(name.lower().find(m[0].lower())!=-1):
						name = m[1]
						break
				for c in country_list:
					if ip_country==c:
						country_count+=1
				if(((name==isp)and(ip_country==country))or((name==isp)and(country=='none')and(country_count<=dist_level))):
					country_list.append(ip_country)
					ret.append(ip[0])
					new_device = True
			except:
				continue
		if not new_device:
			break
		dist_level+=1
	return ret
	
def get_ips_by_city(city):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	ret = []
	ip_list = getIPList()
	for ip in ip_list:
		try:
			record = gi.record_by_addr(ip[0])
			if (str(record['city'])==str(city)):
				ret.append(ip[0])
		except:
			continue
	return ret
	
def get_diversified_ips_by_city(city):
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	gi2 = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	dist_level = 0
	ret = []
	isp_list = []
	ip_list = getIPList()
	while True:
		new_device = False
		for ip in ip_list:
			try:
				isp_count = 0
				new_ip = True
				for r in ret:
					if r==ip[0]:
						new_ip = False
						break
				if not new_ip:
					continue
				name = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
				record = gi2.record_by_addr(ip[0])
				for m in mappings:
					if(name.lower().find(m[0].lower())!=-1):
						name = m[1]
						break
				for isp in isp_list:
					if name==isp:
						isp_count+=1
				if ((str(record['city'])==str(city)) and (isp_count<=dist_level)):
					isp_list.append(name)
					ret.append(ip[0])
					new_device = True
			except:
				continue
		if not new_device:
			break
		dist_level+=1
	return ret
	
def get_ips_by_country(country):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	ret = []
	ip_list = getIPList()
	for ip in ip_list:
		try:
			record = gi.record_by_addr(ip[0])
			if (record['country_name']==country):
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
		new_record = True
		cursor.execute("select SUBSTRING(id,3) from devices where ip='" + ip +"'")
		record = cursor.fetchall()[0][0].lower()
		for r in ret:
			if r == record:
				new_record = False
				break
		if not new_record:
			continue
		ret.append(record)
	conn.close()
	return ret
	
def get_devices_by_ip(ip):
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	cursor.execute("select SUBSTRING(id,3) from devices where ip='" + ip +"'")
	records = cursor.fetchall()
	conn.close()
	return records
	
def get_country_count():
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	country_list = []
	ip_list = getIPList()
	ip_list_active = getIPListActive()
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
				value['count_active']=0
				country_list.append(value)
		except:
			continue
	for ip in ip_list_active:
		try:
			name = gi.country_name_by_addr(ip[0])
			for c in country_list:
				if c['country']==name:
					c['count_active']+=1
		except:
			continue
	return country_list
	

	
def get_city_count():
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	city_list = []
	ip_list = getIPList()
	ip_list_active = getIPListActive()
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
				value['count_active']=0
				city_list.append(value)
		except:
			continue	
	for ip in ip_list_active:
		try:
			rec = gi.record_by_addr(ip[0])
			for c in city_list:
				if ((c['city']==rec['city'])and(c['region']==rec['region_name'])):
					c['count_active']+=1
		except:
			continue
	return city_list
	
def get_provider_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	try:
		isp = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
	except:
		return "unknown"
	for m in mappings:
		if(isp.lower().find(m[0].lower())!=-1):
			isp = m[1]		
	return isp
	
def get_isp_by_device(dev):
	ip = get_ip_by_device(dev)
	return get_provider_by_ip(ip)
	
def get_city_by_ip(ip):
	if len(ip)>0:
		gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
		return gi.record_by_addr(ip[0])
	else:
		return ""
	
def get_isp_count():
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	isp_list = []
	ip_list = getIPList()
	ip_list_active = getIPListActive()
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
				value['count_active']=0
				isp_list.append(value)
		except:
			continue
	for ip in ip_list_active:
		try:
			name = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
			for m in mappings:
				if(name.lower().find(m[0].lower())!=-1):
					name = m[1]
					break
			for isp in isp_list:
				if isp['isp']==name:
					isp['count_active']+=1
		except:
			continue
	return isp_list

def randomize_latitude(lat):
	return (1-((1-(random.random()*2))*.0001))*lat