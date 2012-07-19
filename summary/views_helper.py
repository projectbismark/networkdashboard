from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
from operator import itemgetter

import random
from datetime import datetime, timedelta
from time import time,mktime,strftime

import hashlib
import cvs_helper,datetime_helper,database_helper,geoip_helper

def get_devices_for_compare(device):
	print(device)
	ip = geoip_helper.get_ip_by_device(device)
	print(ip)
	isp = geoip_helper.get_provider_by_ip(ip)
	print(isp)
	#all other ips with this provider
	ips = geoip_helper.get_ips_by_provider(isp)
	print(ips)
	#all other devices with this provider
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

def get_hash(string):
        string = string.replace(':', '')  
        m = hashlib.md5()
        m.update(string)
        return m.hexdigest()
	
def get_sorted_country_data():
	country_data = geoip_helper.get_country_count()
	result = sorted(country_data, key=itemgetter('count'), reverse = True)
	return result
	
def get_sorted_city_data():
	city_data = geoip_helper.get_city_count()
	result = sorted(city_data, key=itemgetter('city'))
	return result
	
def get_sorted_isp_data():
	isp_data = geoip_helper.get_isp_count()
	result = sorted(isp_data, key=itemgetter('count'), reverse = True)
	return result
