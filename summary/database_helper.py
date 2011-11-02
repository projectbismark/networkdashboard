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
import cvs_helper,datetime_helper,views_helper

def fetch_deviceid_soft(device):
	device_search = Devicedetails.objects.filter(deviceid=device)
	try:
		if len(device_search)>0:
			return True
	except:
		pass

	return False
	

def fetch_deviceid_hard(device):
	
	device_search = MBitrate.objects.filter(deviceid=device)
	print device

	try:
		if (len(device_search)>0):
			return True
	except:

		device_search = MRtt.objects.filter(deviceid=device)

	try:
		if (len(device_search)>0):
			return True
	except:
		device_search = MLmrtt.objects.filter(deviceid=device)


	try:
		if (len(device_search)>0):
			return True
	except:
		pass
	
	return False

def list_isps():
	ret = ["Comcast","Time Warner Cable","At&t","Cox Optimum","Charter","Verizon","CenturyLink","SuddenLink","EarthLink","Windstream","Cable One","Frontier","NetZero Juno","Basic ISP","ISP.com","PeoplePC","AOL MSN","Fairpoint","Qwest","CableVision","MEdiaCom"]
	ret.sort()
	return ret

def list_countries():
	ret = ['United States','South Africa','France']
	ret.sort()
	return ret

def get_num_common_locations(device_details):
	return len(Devicedetails.objects.filter(city=device_details.city))-1

def get_num_common_providers(device_details):
	return len(Devicedetails.objects.filter(isp=device_details.isp))-1

def get_num_devices(device_details):
	return len(Devicedetails.objects.exclude(deviceid=device_details.deviceid))-1

def get_first_measurement(device):
	first = MBitrate.objects.filter(deviceid=device).order_by('eventstamp')[0:3]	
    	return first[0].eventstamp.strftime("%B %d, %Y")

def get_last_measurement(device):
	last = MBitrate.objects.filter(deviceid=device).order_by('-eventstamp')[0:3]
    	return last[0].eventstamp.strftime("%B %d, %Y")

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

def get_location(device):
    device = device.replace(':','')
    details = Devicedetails.objects.filter(deviceid=device)
    print details
    if len(details)>0:
        return (details[0].city + ", " + details[0].country)

    dev = MBitrate.objects.filter(deviceid=device, srcip ='143.215.131.173' )
    if len(dev)>0:
        ip = str(dev[0].dstip)
        urlobj=urllib2.urlopen("http://api.ipinfodb.com/v3/ip-city/?key=c91c266accebc12bc7bbdd7fef4b5055c1485208bb6c20b4cc2991e67a3e3d34&ip=" + ip + "&format=json")
        r1 = urlobj.read()
        urlobj.close()
        datadict = json.loads(r1)
        res = datadict["cityName"] + "," + datadict["countryName"]
        return (res)  
    
    return ('unavailable')
		
def save_device_details_from_request(request,device):
    hashing = views_helper.get_hash(device)
    dname = request.POST.get('name')
    disp = request.POST.get('isp')
    dlocation = request.POST.get('location')
    dsp = request.POST.get('sp')
    durate = int(request.POST.get('urate'))
    ddrate = int(request.POST.get('drate'))
    dcity = request.POST.get('city')
    dstate = request.POST.get('state')
    dcountry = request.POST.get('country')	    
       
    details = Devicedetails(deviceid = device, name = dname, isp = disp, serviceplan = dsp, city = dcity, state = dstate, country = dcountry, uploadrate = durate, downloadrate = ddrate, eventstamp = datetime.now(),hashkey=hashing)
    details.save()

def save_device_details_from_default(device):
    hashing = views_helper.get_hash(device)
    device_entry = Devicedetails(deviceid = device,  eventstamp = datetime.now(),name="default name",hashkey=hashing)
    device_entry.save()

def deviceid_to_nodeid(device):
    return "OW" + device.upper()
