from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
from datetime import datetime, timedelta
from time import time,mktime,strftime
import hashlib,httplib,urllib2
import datetime_helper
import ast
import psycopg2
import psycopg2.extras
from django.conf import settings


#looks up a device by its hashkey and returns the deviceid:
def get_device_by_hash(hash):
	device = Devicedetails.objects.get(hashkey=hash)
	if device==None:
		return ''
	return device.deviceid

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

#returns a list containing all unique ISPs among all devices:
def get_all_isps():
	return Devicedetails.objects.values('geoip_isp').distinct()
	
#returns a list containing all unique cities among all devices:
def get_all_cities():
	return Devicedetails.objects.values('geoip_city').distinct()

#searches the provided queryset for deviceids which are not already in devicedetails. If the deviceid
#is missing, a new devicedetails record is created:
def add_new_devices(devices):
	all_details = Devicedetails.objects.all()
	for d in devices:
		#if no devicedetails record with this device id exists:
		if all_details.filter(deviceid=d['deviceid']).count()==0:
			#generate hashkey:
			hash = hashlib.md5()
			hash.update(d['deviceid'])
			hash = hash.hexdigest()
			#create new devicedetails record:
			new_details = Devicedetails(deviceid = d['deviceid'], eventstamp = datetime.now(), hashkey = hash)
			new_details.save()
	return

#returns a list of all distinct countries that have devices:
def get_device_countries():
	return Devicedetails.objects.values('country_code').distinct()

#returns a queryset containing all devices for the given city:
def get_details_by_city(city):
	return Devicedetails.objects.filter(geoip_city=city)

#returns a queryset containing all devices for the given isp:
def get_details_by_isp(isp):
	return Devicedetails.objects.filter(geoip_isp=isp)

#returns a queryset containing all measurement servers:
def get_server_list():
	return IpResolver.objects.all()
	
#calls assign_hash for every device without a hashkey:
def assign_hashkeys():
	unhashed_devices = Devicedetails.objects.filter(hashkey='')
	if unhashed_devices.count()!=0:
		for dev in unhashed_devices:
			assign_hash(dev.deviceid)
	return

#creates and sets a hashkey for a single device:
def assign_hash(device):
	dev = Devicedetails.objects.get(deviceid=device)
	hash = hashlib.md5()
	hash.update(dev.deviceid)
	hash = hash.hexdigest()
	dev.hashkey = hash
	dev.save()
	return

#returns a queryset containing the device with the corresponding id
def get_details_by_deviceid(deviceid):
	device = deviceid.replace(':', '')
	details = Devicedetails.objects.filter(deviceid=device)
	return details

#returns a queryset containing the device with the corresponding hashkey
def get_details_by_hash(hashkey):
	return Devicedetails.objects.filter(hashkey=hashkey)

#returns series of RTT measurements for given device, queries DB directly rather than
#reading from static file:
def get_rtt_measurements(device,days,dstip):
	threading="multi"
	data = []
	end = datetime.now()
	start = datetime_helper.get_daterange_start(int(days))
	rows = MRtt.objects.filter(deviceid=device,dstip=dstip,eventstamp__gte=start,eventstamp__lte=end)
	if len(rows)==0:
		return []
	for r in rows:
		try:
			eventstamp = datetime_helper.datetime_to_JSON(r.eventstamp)
			d = [eventstamp, float(r.average)]
			data.append(d)
		except:
			continue
	return dict(device=device,dstip=dstip,days=days,data=data)

#returns series of LMRTT measurements for given device, queries DB directly rather than
#reading from static file:
def get_lmrtt_measurements(device,days):
	threading = "multi"
	data = []
	end = datetime.now()
	start = datetime_helper.get_daterange_start(int(days))
	rows = MRtt.objects.filter(deviceid=device,eventstamp__gte=start,eventstamp__lte=end)
	if len(rows)==0:
		return []
	for r in rows:
		try:
			eventstamp = datetime_helper.datetime_to_JSON(r.eventstamp)
			d = [eventstamp, float(r.average)]
			data.append(d)
		except:
			continue
	return dict(device=device,days=days,data=data)

#returns series of bitrate measurements for given device, queries DB directly rather than
#reading from static file:
def get_bitrate_measurements(device,days,direction,multi):
	threading = "multi"
	data = []
	end = datetime.now()
	start = datetime_helper.get_daterange_start(int(days))
	rows = MBitrate.objects.filter(deviceid=device,eventstamp__gte=start,eventstamp__lte=end,direction=direction)
	if len(rows)==0:
		return []
	if multi=="1":
		rows = rows.filter(toolid='NETPERF_3')
	else:
		rows = rows.exclude(toolid='NETPERF_3')
		threading = "single"
	for r in rows:
		try:
			eventstamp = datetime_helper.datetime_to_JSON(r.eventstamp)
			d = [eventstamp, float(r.average)]
			data.append(d)
		except:
			continue
	return dict(device=device,days=days,data=data,direction=direction,threading=threading)

#modifies a devicedetails record with the values set on the edit device page:
def save_device_details_from_request(request,device):
	hashing = get_hash(device)
	dname = request.POST.get('name')
	disp = request.POST.get('isp')
	dlocation = request.POST.get('location')
	dsp = request.POST.get('sp')
	dservicetype = request.POST.get('servicetype')
	durate = int(request.POST.get('urate'))
	ddrate = int(request.POST.get('drate'))
	dcity = request.POST.get('city')
	dstate = request.POST.get('state')
	dcountry = request.POST.get('country')        
	details = Devicedetails(deviceid = device, name = dname, isp = disp, serviceplan = dsp, servicetype=dservicetype,city = dcity, state = dstate, country = dcountry, uploadrate = durate, downloadrate = ddrate, eventstamp = datetime.now(),hashkey=hashing)       
	details.is_default=False
	details.save()

#creates a new devicedetails entry. returns True on success:
def save_device_details_from_default(device):
	try:
		hash = hashlib.md5()
		hash.update(device)
		hash = hash.hexdigest()
		device_entry = Devicedetails(
				deviceid=device, eventstamp=datetime.now(), name="default name",
				hashkey=hash, is_default=True)
		device_entry.save()
		return True
	except:
		return False
	
#looks up a device by deviceid and returns its hashkey:
def get_hash(id):
	try:
		device_details = database_helper.get_details_by_deviceid(id)
	#invalid mac address:
	except:
		return ""
	if len(device_details)>0:
		return device_details[0].hashkey
	#no device found:
	else:
		return ""
