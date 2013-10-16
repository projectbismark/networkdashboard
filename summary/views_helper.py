from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
from operator import itemgetter
from django.db import transaction
import random
from datetime import datetime, timedelta
from time import time,mktime,strftime
from django.conf import settings
import psycopg2
import hashlib
import cvs_helper,datetime_helper,database_helper,geoip_helper

#parse coordinates from file for device map: 
def parse_coords():
	coord_data = []
	filename = settings.PROJECT_ROOT + '/summary/measurements/map/coord_data'
	with open(filename,'r') as f:
		for line in f:
			entry = {}
			line = line.replace('\n','')
			line = line.split('|')
			entry['hash'] = line[0]
			entry['lat'] = line[1]
			entry['lon'] = line[2]
			entry['isp'] = line[3]
			entry['active'] = line[4]
			entry['server'] = line[5]
			coord_data.append(entry)
	return coord_data

#returns deviceids for devices matching criteria for comparison bargraph:	
def bargraph_devices_by_city_name(city):
	ips = geoip_helper.bargraph_ips_by_city(city)
	devices = geoip_helper.get_devices_by_ips(ips)
	return devices

#returns deviceids for devices matching criteria for comparison linegraph:	
def linegraph_devices_by_city_name(city,max_results,start,end,metric):
	ips = geoip_helper.linegraph_ips_by_city(city,max_results,start,end,metric)
	devices = geoip_helper.get_devices_by_ips(ips)
	return devices

#returns deviceids for devices matching criteria for comparison bargraph:	
def bargraph_devices_by_country_name(country):
	ips = geoip_helper.bargraph_ips_by_country(country)
	devices = geoip_helper.get_devices_by_ips(ips)
	return devices
	
#returns deviceids for devices matching criteria for comparison bargraph:	
def bargraph_devices_by_provider_and_country(isp,country):
	ips = geoip_helper.bargraph_ips_by_provider_and_country(isp,country)
	devices = geoip_helper.get_devices_by_ips(ips)
	return devices
	
#returns deviceids for devices matching criteria for comparison linegraph:	
def linegraph_devices_by_provider_and_country(isp,country,max_results,start,end,metric):
	ips = geoip_helper.linegraph_ips_by_provider_and_country(isp,country,max_results,start,end,metric)
	devices = geoip_helper.get_devices_by_ips(ips)
	return devices
	
#returns an html page for a particular device for a user who owns that device 
#and forwards data to that page:
def get_response_for_devicehtml(device_details):
	first = database_helper.get_first_measurement(device_details.deviceid)
	last = database_helper.get_last_measurement(device_details.deviceid)
	deviceid = device_details.deviceid.replace(':', '').lower()
	return render_to_response('device.html', {'detail': device_details,'first_update': first, 'last_update': last, 'deviceid': deviceid}) 

#returns an html page for a particular device for a user who does not own that deviec
#and forwards data to that page:
def get_response_for_shared_device(device_details):
	first = database_helper.get_first_measurement(device_details.deviceid)
	last = database_helper.get_last_measurement(device_details.deviceid)
	deviceid = device_details.deviceid.replace(':', '').lower()
	return render_to_response('shared_device.html', {'detail': device_details,'firstUpdate': first, 'lastUpdate': last, 'deviceid': deviceid})
	
#looks up a device by deviceid and returns its hashkey:
def get_hash(id):
	try:
		device_details = Devicedetails.objects.filter(deviceid=id)
	#invalid mac address:
	except:
		return ""
	if len(device_details)>0:
		return device_details[0].hashkey
	#no device found:
	else:
		return ""
		
#gets device counts by country and sorts them alphabetically:
def get_sorted_country_data():
	#get list of dictionaries:
	country_data = geoip_helper.get_country_count()
	result = sorted(country_data, key=itemgetter('country'))
	return result

#gets device counts by city and sorts them alphabetically:	
def get_sorted_city_data():
	#get list of dictionaries:
	city_data = geoip_helper.get_city_count()
	result = sorted(city_data, key=itemgetter('city'))
	return result

#gets device counts by isp and sorts them alphabetically:	
def get_sorted_isp_data():
	#get list of dictionaries:
	isp_data = geoip_helper.get_isp_count()
	result = sorted(isp_data, key=itemgetter('isp'))
	return result

