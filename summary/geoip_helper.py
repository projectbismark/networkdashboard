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

#returns a geoip record for a given IP:
def get_location(ip,gi):
	gi_rec = gi.record_by_addr(ip)
	return gi_rec

#returns latitudinal coordinate for the given IP:
def get_latitude_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	loc = gi.record_by_addr(ip)
	return loc['latitude']

#returns longitudinal coordinate for the given IP:
def get_longitude_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	loc = gi.record_by_addr(ip)
	return loc['longitude']

#returns a list containing the IP of every device:
def get_ip_list():
	devices = Devicedetails.objects.values('deviceid').distinct()
	ips=[]
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" +  settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	for d in devices:
		#formatting for mac address differs between tables Devices and Devicedetails:
		id = "OW" + d['deviceid'].upper().replace(":","")
		params = []
		params.append(id)
		cursor.execute("select ip from devices where id=%s;", params)
		ips.append(cursor.fetchone())
	cursor.close()
	conn.close()
	return ips
	
#returns total number of devices:	
def get_device_count():
	device_count = 0
	filename = settings.PROJECT_ROOT + '/summary/device_data/devices'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			city = line[2]
			country = line[3]
			isp = line[4]
			#to be considered valid, a device's ISP, country, or city must be resolvable from its IP:
			if ((city!=None and city!='') or (country!=None and country!='') or (isp!=None and isp!='')):
				device_count+=1
	return device_count

#returns total number of devices with recent measurements:
def get_active_count():
	active_count = 0
	filename = settings.PROJECT_ROOT + '/summary/device_data/devices'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			#the flag for recently active, set according to threshold defined in update_static_content:
			latest = int(line[5])
			if latest:
				active_count += 1
	return active_count

#resolves IP to city:	
def get_city_by_ip(ip):
	rec = get_record_by_ip(ip)
	if rec != None:
		return rec['city']
	else:
		return ''
		
#uses geoip in an indirect fashion to lookup country by city:
def get_country_by_city(city):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	ips = get_ip_list()
	for ip in ips:
		try:
			record = gi.record_by_addr(ip[0])
			if record['city']==city:
				return record['country_name']
		except:
			continue
	return ''

#resolves IP to country code:
def get_country_code_by_ip(ip):
	rec = get_record_by_ip(ip)
	if rec != None:
		return rec['country_code']
	else:
		return ''

#resolves IP to country name:		
def get_country_name_by_ip(ip):
	rec = get_record_by_ip(ip)
	if rec != None:
		return rec['country_name']
	else:
		return ''

#returns list of dictionaries containing counts for total and active devices for each country:
def get_country_data():
	country_list = []
	filename = settings.PROJECT_ROOT + '/summary/device_data/country_count'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			if len(line)!=3:
				continue
			country = line[0]
			count = line[1]
			active_count = line[2]
			value = {}
			value['country'] = country
			value['count'] = count
			value['count_active'] = active_count
			country_list.append(value)
	return country_list

#returns list of dictionaries containing counts for total and active devices for each city:
def get_city_data():
	city_list = []
	filename = settings.PROJECT_ROOT + '/summary/device_data/city_count'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			if len(line)!=4:
				continue
			city = line[0]
			country = line[1]
			count = line[2]
			active_count = line[3]
			value = {}
			value['city'] = city
			value['country'] = country
			value['count'] = count
			value['count_active'] = active_count
			city_list.append(value)
	return city_list

#returns list of dictionaries containing counts for total and active devices for each isp:
def get_isp_data():
	isp_list = []
	filename = settings.PROJECT_ROOT + '/summary/device_data/isp_count'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			if len(line)!=3:
				continue
			isp = line[0]
			count = line[1]
			active_count = line[2]
			value = {}
			value['isp'] = isp.lstrip()
			value['count'] = count
			value['count_active'] = active_count
			isp_list.append(value)
	return isp_list
	
#resolves IP to ISP:
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

#returns a geoip record for the given IP:
def get_record_by_ip(ip):
	if len(ip)>0:
		gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
		return gi.record_by_addr(ip[0])
	else:
		return ""

#offsets given coordinate by a small, random amount:
def randomize_coordinate(coord):
	return (1-((1-(random.random()*2))*.0001))*coord
