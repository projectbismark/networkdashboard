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

def fetch_deviceid_hard(device):

	device_search = MBitrate.objects.filter(deviceid=device)[0:1]
	
	if (len(device_search)<1):
		device_search = MRtt.objects.filter(deviceid=device)[0:1]

	if (len(device_search)<1):
		device_search = MLmrtt.objects.filter(deviceid=device)[0:1]

	if (len(device_search)<1):
		return False
	else:
		return True

def list_isps():
	ret = ["Comcast","Time Warner Cable","At&t","Cox Optimum","Charter","Verizon","CenturyLink","SuddenLink","EarthLink","Windstream","Cable One","Frontier","NetZero Juno","Basic ISP","ISP.com","PeoplePC","AOL MSN","Fairpoint","Qwest","CableVision","MEdiaCom"]
	ret.sort()
	return ret

def list_countries():
	ret = ['United States','South Africa','France']
	ret.sort()
	return ret

def get_coordinates_for_googlemaps():
 	coordstring = ""

    	distinct_ips = IpResolver.objects.all()

    	for row_ip in distinct_ips:

		lat = str(row_ip.latitude)
		lon = str(row_ip.longitude)
		devtype = str(row_ip.type)
        	coordstring += lat
        	coordstring += ","
        	coordstring += lon
        	coordstring += ","
        	coordstring += devtype
        	coordstring += "\n"
    	return HttpResponse(coordstring)
		
		
	
