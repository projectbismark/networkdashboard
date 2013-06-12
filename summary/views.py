import cvs_helper
import database_helper
import datetime_helper
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Template, Context
from django.utils import simplejson
import email_helper
import geoip_helper
from graph_filter import *
import hashlib
import json
from networkdashboard.summary.models import *
import psycopg2
import random
import site
from time import time,mktime,strftime
import urllib2
import urllib
import views_helper
site.addsitedir("/home/abhishek/.local/lib/python2.6/site-packages/")

def index(request):
	countries = views_helper.get_sorted_country_data()
	cities = views_helper.get_sorted_city_data()
	isps = views_helper.get_sorted_isp_data()
	device_count = views_helper.get_device_count()
	active_count = views_helper.get_active_count()
	return render_to_response('index.html', {'country_data' : countries, 'city_data': cities, 'isp_data': isps, 'device_count':device_count, 'active_count':active_count})
	
def compare(request):
	device = request.POST.get("device").strip("/")
	return render_to_response('compare.html', {'device' : device})
	
def compare_by_city(request, city):
	return render_to_response('compare_by_city.html', {'city' : city})
	
def compare_by_country(request, country):
	return render_to_response('compare_by_country.html', {'country' : country})
	
def compare_by_isp(request, isp):
	return render_to_response('compare_by_isp.html', {'isp' : isp})
	
def compare_bitrate_by_city(request):
	city = request.GET.get('city')
	max_results = int(request.GET.get('max_results'))
	days = int(request.GET.get('days'))
	direction = request.GET.get('direction')
	result = []
	result.append(database_helper.bargraph_compare_bitrate_by_city(city,max_results,days,direction))
	result.append(database_helper.linegraph_compare_bitrate_by_city(city,max_results,days,direction))
	return HttpResponse(json.dumps(result))
	
def compare_bitrate_by_country(request):
	country = request.GET.get('country')
	max_results = int(request.GET.get('max_results'))
	days = int(request.GET.get('days'))
	direction = request.GET.get('direction')
	result = []
	empty = []
	result.append(database_helper.bargraph_compare_bitrate_by_country(country,max_results,days,direction))
	result.append(empty)
	return HttpResponse(json.dumps(result))
	
def compare_bitrate_by_isp(request):
	isp = request.GET.get('isp')
	max_results = int(request.GET.get('max_results'))
	days = int(request.GET.get('days'))
	direction = request.GET.get('direction')
	result = []
	empty = []
	result.append(empty)
	result.append(database_helper.linegraph_compare_bitrate_by_isp(isp,max_results,days,direction))
	return HttpResponse(json.dumps(result))

def compare_lmrtt_by_city(request):
	city = request.GET.get('city')
	max_results = int(request.GET.get('max_results'))
	days = int(request.GET.get('days'))
	result = []
	result.append(database_helper.bargraph_compare_lmrtt_by_city(city,max_results,days))
	result.append(database_helper.linegraph_compare_lmrtt_by_city(city,max_results,days))
	return HttpResponse(json.dumps(result))
	
def compare_lmrtt_by_country(request):
	country = request.GET.get('country')
	max_results = int(request.GET.get('max_results'))
	days = int(request.GET.get('days'))
	result = []
	empty = []
	result.append(database_helper.bargraph_compare_lmrtt_by_country(country,max_results,days))
	result.append(empty)
	return HttpResponse(json.dumps(result))
	
def compare_lmrtt_by_isp(request):
	isp = request.GET.get('isp')
	max_results = int(request.GET.get('max_results'))
	days = int(request.GET.get('days'))
	result = []
	empty = []
	result.append(empty)
	result.append(database_helper.linegraph_compare_lmrtt_by_isp(isp,max_results,days))
	return HttpResponse(json.dumps(result))
	
def compare_rtt_by_city(request):
	city = request.GET.get('city')
	max_results = int(request.GET.get('max_results'))
	days = int(request.GET.get('days'))
	result = []
	result.append(database_helper.bargraph_compare_rtt_by_city(city,max_results,days))
	result.append(database_helper.linegraph_compare_rtt_by_city(city,max_results,days))
	return HttpResponse(json.dumps(result))
		
def compare_rtt_by_country(request):
	country = request.GET.get('country')
	max_results = int(request.GET.get('max_results'))
	days = int(request.GET.get('days'))
	result = []
	empty = []
	result.append(database_helper.bargraph_compare_rtt_by_country(country,max_results,days))
	result.append(empty)
	return HttpResponse(json.dumps(result))
	
def compare_rtt_by_isp(request):
	country = request.GET.get('country')
	max_results = int(request.GET.get('max_results'))
	days = int(request.GET.get('days'))
	result = []
	empty = []
	result.append(empty)
	result.append(database_helper.linegraph_compare_rtt_by_isp(isp,max_results,days))
	return HttpResponse(json.dumps(result))
	
def compare_rtt(request):
	device = request.GET.get('device')
	filter_by = request.GET.get('filter_by')
	criteria = request.GET.get('criteria')
	# The server loc is in this format in compare.html: Latency(server_loc). 
	# Extra characters are removed:
	server_loc = request.GET.get('server_loc').lstrip('Latency( ').strip(')')
	days = int(request.GET.get('days'))
	server_ip = IpResolver.objects.filter(location = server_loc)[0].ip
	devices = views_helper.get_devices_for_compare(device,criteria)
	max_results = int(request.GET.get('max_results'))
	# Calculate earliest date of the series based on user selection:
	earliest = datetime_helper.get_daterange_start(days)
	# Create list of lists. The first list contains data series for the linegraph.
	# The second contains series for the bar graph (averages):
	result = [[] for x in range(2)]
	result_count=0
	data = MRtt.objects.filter(deviceid=device,average__lte=3000,dstip = server_ip, eventstamp__gte=earliest).order_by('eventstamp')
	# Graph data for user's own device:
	graph_data = cvs_helper.linegraph_compare(data,"Your Device",1,1,5)
	result[0].append(graph_data[0])
	result[1].append(graph_data[1])
	for dev in devices:
		if(result_count == max_results):
			break
		# Ignore duplicate graph data for user's own device:
		if dev!= device:
			# Get the most recent RTT measurement for this device:
			latest = MRtt.objects.filter(deviceid=dev,average__lte=3000,dstip = server_ip).order_by('-eventstamp')[:1]
			if len(latest)!=0:
				# Ensure the most recent measurement for this device is not too old:
				if (datetime_helper.is_recent(latest[0].eventstamp,days)):
					data = MRtt.objects.filter(deviceid=dev,average__lte=3000,dstip = server_ip, eventstamp__gte=earliest).order_by('eventstamp')
					graph_data = cvs_helper.linegraph_compare(data,"Other Device",1,1,2)
					result[0].append(graph_data[0])
					result[1].append(graph_data[1])
					result_count +=1
	return HttpResponse(json.dumps(result))
		
def compare_lmrtt(request):
	deviceid = request.GET.get("device")
	criteria = int(request.GET.get("criteria"))
	max_results = int(request.GET.get("max_results"))
	days = int(request.GET.get('days'))
	# Calculate earliest date of the series based on user selection:
	earliest = datetime_helper.get_daterange_start(days)
	devices = views_helper.get_devices_for_compare(deviceid,criteria)
	# Create list of lists. The first list contains data series for the linegraph.
	# The second contains series for the bar graph (averages):
	result = [[] for x in range(2)]
	result_count = 0
	data= MLmrtt.objects.filter(average__lte=3000, deviceid=deviceid, eventstamp__gte=earliest).order_by('eventstamp')
	# Graph data for user's own device:
	graph_data = cvs_helper.linegraph_compare(data,"Your Device",1,1,5)
	result[0].append(graph_data[0])
	result[1].append(graph_data[1])
	for dev in devices:
		if(result_count == max_results):
			break
		# Ignore duplicate graph data for user's own device:
		if dev!= deviceid:
			# Get the most recent RTT measurement for this device:
			latest= MLmrtt.objects.filter(average__lte=3000, deviceid=dev, eventstamp__gte=earliest).order_by('eventstamp')[:1]
			if len(latest)!=0:
				# Ensure the most recent measurement for this device is not too old:
				if (datetime_helper.is_recent(latest[0].eventstamp,days)):
					data= MLmrtt.objects.filter(average__lte=3000, deviceid=dev, eventstamp__gte=earliest).order_by('eventstamp')
					graph_data = cvs_helper.linegraph_compare(data,"Other Device",1,1,2)
					result[0].append(graph_data[0])
					result[1].append(graph_data[1])
					result_count += 1
	return HttpResponse(json.dumps(result))
	
def compare_bitrate(request):
	deviceid = request.GET.get("device")
	criteria = int(request.GET.get("criteria"))
	max_results = int(request.GET.get("max_results"))
	# upload or download:
	dir = request.GET.get("direction")
	days = int(request.GET.get('days'))
	devices = views_helper.get_devices_for_compare(deviceid,criteria)
	# Calculate earliest date of the series based on user selection:
	earliest = datetime_helper.get_daterange_start(days)
	result = [[] for x in range(2)]
	result_count = 0
	data = MBitrate.objects.filter(deviceid = deviceid, direction = dir, toolid = 'NETPERF_3', eventstamp__gte=earliest).order_by('eventstamp')
	# Graph data for user's own device:
	graph_data = cvs_helper.linegraph_compare(data,"Your Device",1000,18000,5)
	result[0].append(graph_data[0])
	result[1].append(graph_data[1])
	for dev in devices:
		if(result_count == max_results):
			break
		# Ignore duplicate graph data for user's own device:
		if dev!= deviceid:
			# Get the most recent RTT measurement for this device:
			latest = MBitrate.objects.filter(deviceid = dev, direction = dir, toolid='NETPERF_3', eventstamp__gte=earliest).order_by('eventstamp')
			if len(latest)!=0:
				# Ensure the most recent measurement for this device is not too old:
				if (datetime_helper.is_recent(latest[0].eventstamp,days)):
					data = MBitrate.objects.filter(deviceid = dev, direction = dir, toolid = 'NETPERF_3', eventstamp__gte=earliest).order_by('eventstamp')
					graph_data = cvs_helper.linegraph_compare(data,"Other Device",1000,18000,2)
					result[0].append(graph_data[0])
					result[1].append(graph_data[1])
					result_count += 1
	return HttpResponse(json.dumps(result))

def editDevicePage(request, devicehash):
    device_details = Devicedetails.objects.filter(hashkey=devicehash)
    if len(device_details) < 1:
        return render_to_response('device_not_found.html', {'devicename' : devicehash})
    device = str(device_details[0].deviceid)
    isp_options = database_helper.list_isps()
    country_options = database_helper.list_countries()
    return render_to_response('edit_device.html', {'detail' : device_details[0], 'deviceid': device, 'isp_options': isp_options, 'country_options': country_options})

def invalidEdit(request, device):
    return render_to_response('invalid_edit.html', {'deviceid' : device})
    
def getCoordinates(request):
	result = geoip_helper.get_coordinates_for_googlemaps()
	return HttpResponse(json.dumps(result))
        
def sharedDeviceSummary(request,devicehash):
    device_details = Devicedetails.objects.filter(hashkey=devicehash)
    if len(device_details)>0:
		device = device_details[0].deviceid		
    else:
		return render_to_response('device_not_found.html', {'deviceid': devicehash})
    return views_helper.get_response_for_shared_device(device_details[0])

def devicesummary(request):
	device = str(request.POST.get("device"))
	device = device.replace(':', '')
	hashing = views_helper.get_hash(device)
	if(request.POST.get("edit")):
		try:
			database_helper.save_device_details_from_request(request,device)
		except:
			return render_to_response('invalid_edit.html', {'deviceid' : hashing})
	#if not database_helper.fetch_deviceid_hard(device):
		#return render_to_response('device_not_found.html', {'deviceid': device})
	device_details = Devicedetails.objects.filter(deviceid=device)
	try: 
		if len(device_details)<1:
			database_helper.save_device_details_from_default(device)
			device_details = Devicedetails.objects.filter(deviceid=device)
	except:
		return render_to_response('device_not_found.html', {'deviceid': device})
		
	return views_helper.get_response_for_devicehtml(device_details[0])

def getLocation(request, device):   
    return HttpResponse(database_helper.get_location(device))

def iptest(iptest):
	dat = geoip_helper.getLocation("117.192.232.202")
	return HttpResponse(str(dat))
	
def linegraph_rtt(request):
	data = []
	device = request.GET.get('deviceid')
	cached_rtt = JsonCache.objects.filter(deviceid=device, datatype='rtt')
	if len(cached_rtt)!=0:
		data = cached_rtt[0].data
	return HttpResponse(data)
	

def linegraph_bitrate(request):
	device = request.GET.get('deviceid')
	graphno = int(request.GET.get('graphno'))
	data = []
	if graphno==1:
		cached_download = JsonCache.objects.filter(deviceid=device, datatype='bitrate_down')
		if len(cached_download)!=0:
			data = cached_download[0].data
	else:
		cached_upload = JsonCache.objects.filter(deviceid=device, datatype='bitrate_up')
		if len(cached_upload)!=0:
			data = cached_upload[0].data
	return HttpResponse(data)

def linegraph_lmrtt(request):
	data = []
	device = request.GET.get('deviceid')
	cached_lmrtt = JsonCache.objects.filter(deviceid=device, datatype='lmrtt')
	if len(cached_lmrtt)!=0:
		data = cached_lmrtt[0].data
	return HttpResponse(data)

def linegraph_shaperate(request):
	data = []
	device = request.GET.get('deviceid')
	cached_shaperate = JsonCache.objects.filter(deviceid=device, datatype='shaperate')
	cached_capacity = JsonCache.objects.filter(deviceid=device, datatype='capacity')
	if len(cached_shaperate)!=0:
		shaperate_data = json.loads(cached_shaperate[0].data)
		# append both shaperate series
		for series in shaperate_data:
			data.append(series)
		if len(cached_capacity)!=0:
			capacity_data = json.loads(cached_capacity[0].data)
			# append both capacity series
			for series in capacity_data:
				data.append(series)
	return HttpResponse(json.dumps(data))

def linegraph_unload(request):
	data = []
	device = request.GET.get('deviceid')
	cached_unload = JsonCache.objects.filter(deviceid=device, datatype='unload')
	if len(cached_unload)!=0:
		data = cached_unload[0].data
	return HttpResponse(data)
	
  
def feedback(request):
	return render_to_response('feedback.html', {'hashkey' : request.GET.get('hashkey')})

def send_feedback(request):

	has = request.POST.get('hashkey')
	sender = request.POST.get('sender')
	message = request.POST.get('message')

	try:
		email_helper.send_email(has,sender,message)
	except:
	
		return HttpResponse("your feedback is on its way. Thank you!")
	
	return HttpResponse("feedback received. Thank you!")

'''
80	80	Web
443	443	HTTPS
993	993	IMAPS
587	587	SMTPS
995	995	POP3S
5223	5223	JABBER
53	53	DNS
25	25	SMTP
22	22	SSH
'''
