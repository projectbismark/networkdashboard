from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
from pyofc2 import *
import random
from datetime import datetime, timedelta
from time import time,mktime,strftime
from mx.DateTime.ISO import ParseDateTimeUTC
import hashlib
import cvs_helper,datetime_helper,database_helper

def get_response_for_devicehtml(device_details):

    first = database_helper.get_first_measurement(device_details.deviceid)
    last = database_helper.get_last_measurement(device_details.deviceid)

    num_location = database_helper.get_num_common_locations(device_details)
    num_provider = database_helper.get_num_common_providers(device_details)
    num_all = database_helper.get_num_devices(device_details)

    device_details.deviceid =  device_details.deviceid.replace(':', '')
	
    return render_to_response('device.html', {'detail': device_details,'firstUpdate': first, 'lastUpdate': last, 'deviceid': device_details.deviceid, 'num_location' : num_location, 'num_provider' : num_provider, 'num_all' : num_all}) 

def get_hash(string):
    string = string.replace(':', '')  
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()
