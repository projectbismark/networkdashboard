from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *

import random
from datetime import datetime, timedelta
from time import time,mktime,strftime

import hashlib
import cvs_helper,datetime_helper,database_helper

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
