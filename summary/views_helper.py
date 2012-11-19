from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
from operator import itemgetter
from django.db import transaction
import random
from datetime import datetime, timedelta
from time import time,mktime,strftime

import hashlib
import cvs_helper,datetime_helper,database_helper,geoip_helper

def get_devices_for_compare(device,criteria):
	if (criteria==1):
		return get_devices_by_isp(device)
	else:
		return get_devices_by_city(device)
	
def get_devices_by_isp(device):
	ip = geoip_helper.get_ip_by_device(device)
	isp = geoip_helper.get_provider_by_ip(ip)
	#all other ips with this provider
	ips = geoip_helper.get_ips_by_provider(isp)
	#devices for these ips
	devices = geoip_helper.get_devices_by_ips(ips)
	return devices
	
def get_devices_by_city(device):
	ip = geoip_helper.get_ip_by_device(device)
	city = geoip_helper.get_city_by_ip(ip)
	#all other ips with this city
	ips = geoip_helper.get_ips_by_city(city)
	#devices for these ips
	devices = geoip_helper.get_devices_by_ips(ips)
	return devices
	

def get_response_for_devicehtml(device_details):

	first = database_helper.get_first_measurement(device_details.deviceid)
	last = database_helper.get_last_measurement(device_details.deviceid)
	num_location = database_helper.get_num_common_locations(device_details)
	num_provider = database_helper.get_num_common_providers(device_details)
	num_all = database_helper.get_num_devices(device_details)
	latest_download = database_helper.get_latest_download(device_details.deviceid)
	latest_upload = database_helper.get_latest_upload(device_details.deviceid)
	latest_lastmile = database_helper.get_latest_lastmile(device_details.deviceid)
	latest_roundtrip = database_helper.get_latest_roundtrip(device_details.deviceid)
	latest_shaperate = database_helper.get_latest_shaperate(device_details.deviceid)
	device_details.deviceid = device_details.deviceid.replace(':', '').lower()
	return render_to_response('device.html', {'detail': device_details,'firstUpdate': first, 'lastUpdate': last, 'deviceid': device_details.deviceid, 'num_location' : num_location, 'num_provider' : num_provider, 'num_all' : num_all, 'latestdownload' : latest_download, 'latestupload' : latest_upload, 'latestlastmile' : latest_lastmile, 'latestroundtrip' : latest_roundtrip, 'latestshaperate': latest_shaperate}) 

def get_response_for_shared_device(device_details):
	first = database_helper.get_first_measurement(device_details.deviceid)
	last = database_helper.get_last_measurement(device_details.deviceid)
	num_location = database_helper.get_num_common_locations(device_details)
	num_provider = database_helper.get_num_common_providers(device_details)
	num_all = database_helper.get_num_devices(device_details)
	latest_download = database_helper.get_latest_download(device_details.deviceid)
	latest_upload = database_helper.get_latest_upload(device_details.deviceid)
	latest_lastmile = database_helper.get_latest_lastmile(device_details.deviceid)
	latest_roundtrip = database_helper.get_latest_roundtrip(device_details.deviceid)
	latest_shaperate = database_helper.get_latest_shaperate(device_details.deviceid)
	device_details.deviceid = device_details.deviceid.replace(':', '').lower()
	return render_to_response('shared_device.html', {'detail': device_details,'firstUpdate': first, 'lastUpdate': last, 'deviceid': device_details.deviceid, 'num_location' : num_location, 'num_provider' : num_provider, 'num_all' : num_all, 'latestdownload' : latest_download, 'latestupload' : latest_upload, 'latestlastmile' : latest_lastmile, 'latestroundtrip' : latest_roundtrip, 'latestshaperate': latest_shaperate}) 

# def get_hash(string):
	# string = string.replace(':', '')
	# m = hashlib.md5()
	# m.update(string)
	# return m.hexdigest()
	
# def get_hash(id):
	# devices = Devicedetails.objects.all()
	# if len(id)>1:
		# id = id[0]
	# elif len(id)==0:
		# return ""
	# for d in devices:
		# deviceid = str(d.deviceid).replace(':','')
		# if(id[0][0].lower()==deviceid):
			# return d.hashkey
	# return ""
	
def get_hash(id):
	if len(id)>1:
		id = id[0]
	elif len(id)==0:
		return ""
	id = str(id[0][0])
	if len(id)!=12:
		return ""
	id = ':'.join([id[i:i+2] for i in range(0, len(id)-1, 2)]).lower()
	device_details = Devicedetails.objects.filter(deviceid=id)
	if len(device_details)>0:
		return device_details[0].hashkey
	else:
		return ""
	
def get_device_count():
	return geoip_helper.get_device_count()
	
def get_sorted_country_data():
	country_data = geoip_helper.get_country_count()
	result = sorted(country_data, key=itemgetter('count'), reverse = True)
	return result
	
def get_sorted_city_data():
	city_data = geoip_helper.get_city_count()
	result = sorted(city_data, key=itemgetter('count'), reverse = True)
	return result
	
def get_sorted_isp_data():
	isp_data = geoip_helper.get_isp_count()
	result = sorted(isp_data, key=itemgetter('count'), reverse = True)
	return result
