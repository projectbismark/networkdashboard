import cvs_helper
import database_helper
import datetime_helper
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
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
	active_threshold = datetime_helper.get_daterange_start(200)
	active_count = MBitrate.objects.filter(eventstamp__gte=active_threshold).values('deviceid').distinct().count()
	return render_to_response('index.html', {'country_data' : countries, 'city_data': cities, 'isp_data': isps, 'device_count':device_count, 'active_count':active_count})
	
def compare(request):
	device = request.POST.get("device").strip("/")
	servers = IpResolver.objects.all()	
	return render_to_response('compare.html', {'device' : device, 'servers' : servers})
		
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
				# Ensure the most recent measurement for this device is no older than 10 days:
				if (datetime_helper.is_recent(latest[0].eventstamp,10)):
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
				# Ensure the most recent measurement for this device is no older than 10 days:
				if (datetime_helper.is_recent(latest[0].eventstamp,10)):
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
				# Ensure the most recent measurement for this device is no older than 10 days:
				if (datetime_helper.is_recent(latest[0].eventstamp,10)):
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
	if not database_helper.fetch_deviceid_hard(device):
		return render_to_response('device_not_found.html', {'deviceid': device})
	device_details = Devicedetails.objects.filter(deviceid=device)
	print "dev details"
	print device_details
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
	rtt_data=[]
	series_id=3
	priority=0
	device = request.GET.get('deviceid')
	cache = JsonCache.objects.filter(deviceid=device, datatype = "rtt")
	# cache contains cached data:
	if len(cache)!=0:
		# this will hold the latest measurement for each series
		latest_measurements = []
		rtt_data = eval(cache[0].data)
		for series in rtt_data:
			latest_measurements.append(datetime.utcfromtimestamp(int(series['data'][-1][0])/1000))
		# determine which measurement was most recently cached:
		most_recent_measure = max(latest_measurements)
		# retrieve all uncached measurements:
		full_details = MRtt.objects.filter(deviceid=device,average__lte=3000,eventstamp__gt=most_recent_measure)
		distinct_ips = full_details.values('dstip').distinct()
		full_details = full_details.order_by('eventstamp')
		# all measurements are already cached:
		if len(full_details)==0:
			return HttpResponse(json.dumps(rtt_data))
		for ip in distinct_ips:
			try:
				ip_lookup = IpResolver.objects.filter(ip=ip['dstip'])[0]
				dst_ip = ip_lookup.ip
				# bandaid fix - the series derives its name from the location field of table ip_resolver
				# and currently there are at least 2 records with the same location in this table:
				if (dst_ip == '4.71.254.153'):
					location = 'Atlanta, GA (2)'
				else:
					location = ip_lookup.location
			except:
				continue
			device_details = full_details.filter(dstip = ip['dstip'])		
			if len(device_details)==0:
				continue
			if(location=="Georgia Tech"):
				priority=1
			else:
				priority=0
			#find the correct series in the cache data to append to:
			for index in range(len(rtt_data)):
				if rtt_data[index]['name']==location:
					rtt_data[index]['data'].extend(cvs_helper.linegraph_normal(device_details,ip_lookup,1,1,priority,series_id)['data'])
					break
				# new series:
				if (index==(len(rtt_data)-1)):
					rtt_data.append(cvs_helper.linegraph_normal(device_details,ip_lookup,1,1,priority,series_id))
		cache.data = rtt_data
		cache.save()
		return HttpResponse(json.dumps(rtt_data))
	# cache is empty:
	else:
		full_details = MRtt.objects.filter(deviceid=device,average__lte=3000)
		distinct_ips = full_details.values('dstip').distinct()
		# must wait until after distinct query before ordering original queryset:
		full_details = full_details.order_by('eventstamp')
		for ip in distinct_ips:
			try:
				ip_lookup = IpResolver.objects.filter(ip=ip['dstip'])[0]
				dst_ip = ip_lookup.ip
				# bandaid fix - the series derives its name from the location field of table ip_resolver
				# and currently there are at least 2 records with the same location in this table:
				if (dst_ip == '4.71.254.153'):
					location = 'Atlanta, GA (2)'
				else:
					location = ip_lookup.location	
			except:
				continue
			device_details = full_details.filter(dstip = ip['dstip'])		
			if len(device_details)==0:
				continue
			if(location=="Georgia Tech"):
				priority=1
			else:
				priority=0
			rtt_data.append(cvs_helper.linegraph_normal(device_details,location,1,1,priority,series_id))
		cache_new = JsonCache(deviceid = device, data = rtt_data, datatype = 'rtt')
		cache_new.save()
		
		return HttpResponse(json.dumps(rtt_data))

def linegraph_bitrate(request):
	g_filter = Graph_Filter(request)
	chosen_limit = 100000000
	most_recent = []
	# get all cached data:
	cache_down = JsonCache.objects.filter(deviceid=g_filter.device, datatype = "bitrate_down")
	cache_up = JsonCache.objects.filter(deviceid=g_filter.device, datatype = "bitrate_up")
	# both caches already contain cached data:
	if (len(cache_down)!=0 and len(cache_up)!=0):
		download_data = eval(cache_down[0].data)
		upload_data = eval(cache_up[0].data)
		# split into the seperate series, multi-threaded and single-threaded:
		download_multi = download_data[0]
		download_single = download_data[1]
		upload_multi = upload_data[0]
		upload_single = upload_data[1]
		# get timestamp of most recent measurement for each of the 4 series:
		most_recent.append(datetime.utcfromtimestamp(int(download_multi['data'][-1][0])/1000))
		most_recent.append(datetime.utcfromtimestamp(int(download_single['data'][-1][0])/1000))
		most_recent.append(datetime.utcfromtimestamp(int(upload_multi['data'][-1][0])/1000))
		most_recent.append(datetime.utcfromtimestamp(int(upload_single['data'][-1][0])/1000))
		# determine which measurement was most recently cached:
		most_recent_measure = max(most_recent)
		# retrieve all uncached measurements:
		all_device_details= MBitrate.objects.filter(average__lte=chosen_limit,deviceid=g_filter.device,eventstamp__gt=most_recent_measure).order_by('eventstamp')
		# if there are no uncached measurements:
		if len(all_device_details)==0:
			if (g_filter.graphno==1):
				data = download_data
			else:
				data = upload_data
			return HttpResponse(json.dumps(data))
		downloads = all_device_details.filter(direction='dw')
		uploads = all_device_details.filter(direction='up')
		downloads_netperf_3 = downloads.filter(toolid='NETPERF_3').order_by('eventstamp')
		downloads_other = downloads.exclude(toolid='NETPERF_3').order_by('eventstamp')
		uploads_netperf_3 = downloads.filter(toolid='NETPERF_3').order_by('eventstamp')
		uploads_other = downloads.exclude(toolid='NETPERF_3').order_by('eventstamp')
		download_data[0]['data'].extend(cvs_helper.linegraph_normal(downloads_netperf_3,"Multi-threaded TCP",1000,18000,1,1)['data'])
		download_data[1]['data'].extend(cvs_helper.linegraph_normal(downloads_other,"Single-threaded TCP",1000,18000,0,1)['data'])
		upload_data[0]['data'].extend(cvs_helper.linegraph_normal(uploads_netperf_3,"Multi-threaded TCP",1000,18000,1,2)['data'])
		upload_data[1]['data'].extend(cvs_helper.linegraph_normal(uploads_other,"Single-threaded TCP",1000,18000,0,2)['data'])
		cache_down[0].data=download_data
		cache_up[0].data=upload_data
		cache_down[0].save()
		cache_up[0].save()
		# even though both upload and download measurements are cached, only one set of measurements is expected by the graph:
		if (g_filter.graphno==1):
			data = download_data
		else:
			data = upload_data
		return HttpResponse(json.dumps(data))
	# 1 or both caches are empty:
	else:
		# check whether caches are empty or not. If only 1 cache is empty, trying to append to the data
		# portion of the non-empty cache would corrupt the cache. These are booleans which evaluate to true
		# in the event that the respective cache is indeed empty:
		cache_check_down = len(JsonCache.objects.filter(deviceid=g_filter.device, datatype = "bitrate_down"))==0
		cache_check_up = len(JsonCache.objects.filter(deviceid=g_filter.device, datatype = "bitrate_up"))==0
		all_device_details= MBitrate.objects.filter(average__lte=chosen_limit,deviceid=g_filter.device).order_by('eventstamp')
		# no measurements exist at all:
		if len(all_device_details)==0:
			return HttpResponse(json.dumps([]))
		downloads = all_device_details.filter(direction='dw')
		uploads = all_device_details.filter(direction='up')
		downloads_netperf_3 = downloads.filter(toolid='NETPERF_3').order_by('eventstamp')
		downloads_other = downloads.exclude(toolid='NETPERF_3').order_by('eventstamp')
		uploads_netperf_3 = uploads.filter(toolid='NETPERF_3').order_by('eventstamp')
		uploads_other = uploads.exclude(toolid='NETPERF_3').order_by('eventstamp')
		download_data = []
		upload_data = []
		download_data.append(cvs_helper.linegraph_normal(downloads_netperf_3,"Multi-threaded TCP",1000,18000,1,1))
		download_data.append(cvs_helper.linegraph_normal(downloads_other,"Single-threaded TCP",1000,18000,0,1))
		upload_data.append(cvs_helper.linegraph_normal(uploads_netperf_3,"Multi-threaded TCP",1000,18000,1,2))
		upload_data.append(cvs_helper.linegraph_normal(uploads_other,"Single-threaded TCP",1000,18000,0,2))
		if (cache_check_down):
			cache_down_new = JsonCache(deviceid = g_filter.device, data = download_data, datatype = 'bitrate_down')
			cache_down_new.save()	
		if (cache_check_up):
			cache_up_new = JsonCache(deviceid = g_filter.device, data = upload_data, datatype = 'bitrate_up')
			cache_up_new.save()
		# even though both upload and download measurements are cached, only one set of measurements is expected by the graph:
		if (g_filter.graphno==1):
			data = download_data
		else:
			data = upload_data
		return HttpResponse(json.dumps(data))

def linegraph_lmrtt(request):
	lmrtt_data=[]
	series_id=4
	device = request.GET.get('deviceid')
	lmrtt_cache = JsonCache.objects.filter(deviceid=device, datatype='lmrtt')
	if len(lmrtt_cache)!=0:
		lmrtt_data = eval(lmrtt_cache[0].data)
		latest_measurement = datetime.utcfromtimestamp(int(lmrtt_data[0]['data'][-1][0])/1000)
		uncached_measurements = MLmrtt.objects.filter(deviceid=device,average__lte=3000,eventstamp__gt=latest_measurement).order_by('eventstamp')
		# cache is up to date:
		if (len(uncached_measurements)==0):
			return HttpResponse(json.dumps(lmrtt_data))
		lmrtt_data[0]['data'].extend(cvs_helper.linegraph_normal(uncached_measurements,'Last mile latency',1,1,1,series_id)['data'])
		lmrtt_cache[0].data = lmrtt_data
		lmrtt_cache[0].save()
		return HttpResponse(json.dumps(lmrtt_data))
	else:
		all_measurements = MLmrtt.objects.filter(deviceid=device,average__lte=3000).order_by('eventstamp')
		# no measurements for this device
		if len(all_measurements)==0:
			return HttpResponse(json.dumps(lmrtt_data))
		lmrtt_data.append(cvs_helper.linegraph_normal(all_measurements,'Last mile latency',1,1,1,series_id))
		new_cache = JsonCache(deviceid = device, data = lmrtt_data, datatype = 'lmrtt')
		new_cache.save()
		return HttpResponse(json.dumps(lmrtt_data))

def linegraph_shaperate(request):
	series_id=5
	# series data for shaperate, in json format:
	shaperate_data = []
	# series data for capacity, in json format:
	capacity_data = []
	device = request.GET.get('deviceid')
	# retrieve cached data:
	shaperate_cache = JsonCache.objects.filter(deviceid=device,datatype='shaperate')
	capacity_cache = JsonCache.objects.filter(deviceid=device,datatype='capacity')
	# both caches already contain cached data:
	if (len(shaperate_cache)!=0 and len(capacity_cache)!=0):
		shaperate_data = eval(shaperate_cache[0].data)
		capacity_data = eval(capacity_cache[0].data)
		# split into 4 separate series, upload and download for shaperate and capacity:
		shaperate_up = shaperate_data[0]
		shaperate_down = shaperate_data[1]
		capacity_up = capacity_data[0]
		capacity_down = capacity_data[1]
		# get timestamp of most recent measurement for each of the 4 series:
		recent_shaperate_up = datetime.utcfromtimestamp(int(shaperate_up['data'][-1][0])/1000)
		recent_shaperate_down = datetime.utcfromtimestamp(int(shaperate_down['data'][-1][0])/1000)
		recent_capacity_up = datetime.utcfromtimestamp(int(capacity_up['data'][-1][0])/1000)
		recent_capacity_down = datetime.utcfromtimestamp(int(capacity_down['data'][-1][0])/1000)
		# determine which measurements were most recently cached:
		most_recent_shaperate = max(recent_shaperate_up, recent_shaperate_down)
		most_recent_capacity = max(recent_capacity_up, recent_capacity_down)
		# retrieve all uncached measurements:
		uncached_shaperate = MShaperate.objects.filter(deviceid=device,eventstamp__gt=most_recent_shaperate).order_by('eventstamp')
		uncached_capacity = MCapacity.objects.filter(deviceid=device,eventstamp__gt=most_recent_capacity).order_by('eventstamp')
		if len(uncached_shaperate)!=0:
			# separate shaperate records into upload and download
			shape_measure_up = uncached_shaperate.filter(direction='up').order_by('eventstamp')
			shape_measure_down = uncached_shaperate.filter(direction='dw').order_by('eventstamp')
			# convert records to series data and append to cached data:
			shaperate_data[0]['data'].extend(cvs_helper.linegraph_normal(shape_measure_up,'Shape rate Up',1000,1,0,series_id)['data'])
			shaperate_data[1]['data'].extend(cvs_helper.linegraph_normal(shape_measure_down,'Shape rate Down',1000,1,1,series_id)['data'])
			shaperate_cache[0].data=shaperate_data
			shaperate_cache[0].save()
		if len(uncached_capacity)!=0:
			cap_measure_up = uncached_capacity.filter(direction='up').order_by('eventstamp')
			cap_measure_down = uncached_capacity.filter(direction='dw').order_by('eventstamp')
			capacity_data[0]['data'].extend(cvs_helper.linegraph_normal(cap_measure_up,'Capacity Up',1000,1,0,series_id)['data'])
			capacity_data[1]['data'].extend(cvs_helper.linegraph_normal(cap_measure_down,'Capacity Down',1000,1,0,series_id)['data'])
			capacity_cache[0].data=capacity_data
			capacity_cache[0].save()
	# 1 or both caches are empty:
	else:
		# check whether caches are empty or not. If only 1 cache is empty, trying to append to the data
		# portion of the non-empty cache would corrupt the cache. These are booleans which evaluate to true
		# in the event that the respective cache is indeed empty:
		cache_check_shape = len(JsonCache.objects.filter(deviceid=device, datatype = 'shaperate'))==0
		cache_check_cap = len(JsonCache.objects.filter(deviceid=device, datatype = 'capacity'))==0
		# retrieve all capacity and shaperate measurement records for this device:
		all_shaperate= MShaperate.objects.filter(deviceid=device).order_by('eventstamp')
		all_capacity= MCapacity.objects.filter(deviceid=device).order_by('eventstamp')
		if len(all_shaperate)!=0:
			# separate shaperate records into upload and download:
			shape_measure_up = all_shaperate.filter(direction='up')
			shape_measure_down = all_shaperate.filter(direction='dw')
			# convert records into new series to be placed in cache:
			shaperate_data.append(cvs_helper.linegraph_normal(shape_measure_up,'Shape rate Up',1000,1,0,series_id))
			shaperate_data.append(cvs_helper.linegraph_normal(shape_measure_down,'Shape rate Down',1000,1,1,series_id))
			# if cache is empty:
			if (cache_check_shape):
				cache_shaperate_new = JsonCache(deviceid = device, data = shaperate_data, datatype = 'shaperate')
				cache_shaperate_new.save()
		if len(all_capacity)!=0:
			cap_measure_up = all_capacity.filter(direction='up')
			cap_measure_down = all_capacity.filter(direction='dw')
			capacity_data.append(cvs_helper.linegraph_normal(cap_measure_up,'Capacity Up',1000,1,0,series_id))
			capacity_data.append(cvs_helper.linegraph_normal(cap_measure_down,'Capacity Down',1000,1,0,series_id))
			if (cache_check_cap):
				cache_capacity_new = JsonCache(deviceid = device, data =capacity_data, datatype = 'capacity')
				cache_capacity_new.save()
	shaperate_data.extend(capacity_data)
	return HttpResponse(json.dumps(shaperate_data))
  
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
