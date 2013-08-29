from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
import random
from datetime import datetime, timedelta
from time import time,mktime,strftime
import hashlib,httplib,urllib2
import cvs_helper,datetime_helper,geoip_helper, views_helper
import ast
import psycopg2
import psycopg2.extras
from django.conf import settings

# searches the provided queryset for deviceids which are not already in devicedetails. If the deviceid
# is missing, a new devicedetails record is created:
def add_new_devices(devices):
	all_details = Devicedetails.objects.all()
	for d in devices:
		# if no devicedetails record with this device id exists:
		if all_details.filter(deviceid=d['deviceid']).count()==0:
			# generate hashkey:
			hash = hashlib.md5()
			hash.update(d['deviceid'])
			hash = hash.hexdigest()
			# create new devicedetails record:
			new_details = Devicedetails(deviceid = d['deviceid'], eventstamp = datetime.now(), hashkey = hash)
			new_details.save()
	return

# appends new bitrate measurements to precomputed (cached) JSON dictionaries for each device. This method updates
# a db record and returns nothing.
def update_bitrate(device):
	chosen_limit = 100000000
	most_recent = []
	# get all cached data:
	cache_down = JsonCache.objects.filter(deviceid=device, datatype = "bitrate_down")
	cache_up = JsonCache.objects.filter(deviceid=device, datatype = "bitrate_up")
	# both caches already contain cached data:
	if (cache_down.count()!=0 and cache_up.count()!=0):
		most_recent_cached = cache_down[0].eventstamp
		all_device_details= MBitrate.objects.filter(average__lte=chosen_limit,deviceid=device, eventstamp__gt=most_recent_cached)
		# no new measurements for this device:
		if (all_device_details.count())==0:
			return
		most_recent_measure = all_device_details.latest('eventstamp').eventstamp
		all_device_details = all_device_details.order_by('eventstamp')
		# cache is up to date
		# if most_recent_measure<=most_recent_cached:
			# return
		download_data = json.loads(cache_down[0].data)
		upload_data = json.loads(cache_up[0].data)
		# split into the seperate series, multi-threaded and single-threaded:
		download_multi = download_data[0]
		download_single = download_data[1]
		upload_multi = upload_data[0]
		upload_single = upload_data[1]
		# retrieve all uncached measurements:
		# all_device_details= all_device_details.filter(eventstamp__gt=most_recent_cached)
		# if there are no uncached measurements:
		if (all_device_details.count())==0:
			return
		downloads = all_device_details.filter(direction='dw')
		uploads = all_device_details.filter(direction='up')
		downloads_netperf_3 = downloads.filter(toolid='NETPERF_3')
		downloads_other = downloads.exclude(toolid='NETPERF_3')
		uploads_netperf_3 = uploads.filter(toolid='NETPERF_3')
		uploads_other = uploads.exclude(toolid='NETPERF_3')
		download_data[0]['data'].extend(cvs_helper.linegraph_normal(downloads_netperf_3,"Multi-threaded TCP",1000,18000,1,1)['data'])
		download_data[1]['data'].extend(cvs_helper.linegraph_normal(downloads_other,"Single-threaded TCP",1000,18000,0,1)['data'])
		upload_data[0]['data'].extend(cvs_helper.linegraph_normal(uploads_netperf_3,"Multi-threaded TCP",1000,18000,1,2)['data'])
		upload_data[1]['data'].extend(cvs_helper.linegraph_normal(uploads_other,"Single-threaded TCP",1000,18000,0,2)['data'])
		id_down = cache_down[0].id
		id_up = cache_up[0].id
		deviceid = cache_down[0].deviceid
		update_down = JsonCache(id=id_down,deviceid=deviceid,eventstamp=most_recent_measure,datatype="bitrate_down",data=json.dumps(download_data))
		update_up = JsonCache(id=id_up,deviceid=deviceid,eventstamp=most_recent_measure,datatype="bitrate_up", data=json.dumps(upload_data))
		update_down.save()
		update_up.save()
		# cache_down[0].data=json.dumps(download_data)
		# cache_down[0].eventstamp = most_recent_measure
		# cache_up[0].data= json.dumps(upload_data)
		# cache_up[0].eventstamp = most_recent_measure
		# cache_down[0].save()
		# cache_up[0].save()
		return
	# 1 or both caches are empty:
	else:
		# check whether caches are empty or not. If only 1 cache is empty, trying to append to the data
		# portion of the non-empty cache would corrupt the cache. These are booleans which evaluate to true
		# in the event that the respective cache is indeed empty:
		cache_check_down = JsonCache.objects.filter(deviceid=device, datatype = "bitrate_down").count()==0
		cache_check_up = JsonCache.objects.filter(deviceid=device, datatype = "bitrate_up").count()==0
		all_device_details= MBitrate.objects.filter(average__lte=chosen_limit,deviceid=device)
		# no measurements exist at all:
		if all_device_details.count()==0:
			return
		all_device_details = all_device_details.order_by('eventstamp')
		most_recent_measure = all_device_details.latest('eventstamp').eventstamp
		downloads = all_device_details.filter(direction='dw')
		uploads = all_device_details.filter(direction='up')
		downloads_netperf_3 = downloads.filter(toolid='NETPERF_3')
		downloads_other = downloads.exclude(toolid='NETPERF_3')
		uploads_netperf_3 = uploads.filter(toolid='NETPERF_3')
		uploads_other = uploads.exclude(toolid='NETPERF_3')
		download_data = []
		upload_data = []
		download_data.append(cvs_helper.linegraph_normal(downloads_netperf_3,"Multi-threaded TCP",1000,18000,1,1))
		download_data.append(cvs_helper.linegraph_normal(downloads_other,"Single-threaded TCP",1000,18000,0,1))
		upload_data.append(cvs_helper.linegraph_normal(uploads_netperf_3,"Multi-threaded TCP",1000,18000,1,2))
		upload_data.append(cvs_helper.linegraph_normal(uploads_other,"Single-threaded TCP",1000,18000,0,2))
		if (cache_check_down):
			cache_down_new = JsonCache(deviceid = device, data = json.dumps(download_data), datatype = 'bitrate_down', eventstamp = most_recent_measure)
			cache_down_new.save()	
		if (cache_check_up):
			cache_up_new = JsonCache(deviceid = device, data = json.dumps(upload_data), datatype = 'bitrate_up', eventstamp = most_recent_measure)
			cache_up_new.save()
		return

# appends new rtt measurements to precomputed (cached) JSON dictionaries for each device. This method updates
# a db record and returns nothing. 		
def update_rtt(device):
	rtt_data=[]
	series_id=3
	priority=0
	cache = JsonCache.objects.filter(deviceid=device, datatype = "rtt")
	# cache contains cached data:
	if (cache.count())!=0:
		most_recent_cached = cache.latest('eventstamp').eventstamp
		full_details = MRtt.objects.filter(deviceid=device,average__lte=3000, eventstamp__gt=most_recent_cached)
		if full_details.count()==0:
			return
		#full_details = full_details.order_by('eventstamp')
		most_recent_uncached = full_details.latest('eventstamp').eventstamp
		# if (most_recent_uncached<=most_recent_cached):
			# return
		rtt_data = json.loads(cache[0].data)
		# retrieve all uncached measurements:
		distinct_ips = full_details.distinct('dstip').values('dstip')
		# full_details = full_details.filter(eventstamp__gt=most_recent_cached).order_by('eventstamp')
		location = ''
		dst_ip = ''
		for ip in distinct_ips:
			dst_ip = ip['dstip']
			try:
				ip_lookup = IpResolver.objects.filter(ip=dst_ip)
				# not an active measurement server:
				if (ip_lookup.count())==0:
					continue
				else:
					location = ip_lookup[0].location
			except:
				continue
			device_details = full_details.filter(dstip = ip['dstip'])
			if (device_details.count())==0:
				continue
			if(location=="Georgia Tech"):
				priority=1
			else:
				priority=0
			#find the correct series in the cache data to append to:
			for index in range(len(rtt_data)):
				if rtt_data[index]['name']==location:
					rtt_data[index]['data'].extend(cvs_helper.linegraph_normal(device_details,location,1,1,priority,series_id)['data'])
					break
				# new series:
				if (index==(len(rtt_data)-1)):
					rtt_data.append(cvs_helper.linegraph_normal(device_details,location,1,1,priority,series_id))
		id = cache[0].id
		deviceid = cache[0].deviceid
		cache_update = JsonCache(deviceid=deviceid,id=id,eventstamp=most_recent_uncached,data=json.dumps(rtt_data),datatype='rtt')
		#cache[0].data = json.dumps(rtt_data)
		#cache[0].eventstamp = most_recent_uncached
		#cache[0].save()
		cache_update.save()
		return
	# cache is empty:
	else:
		full_details = MRtt.objects.filter(deviceid=device,average__lte=3000)
		if full_details.count()==0:
			return
		most_recent = full_details.latest('eventstamp').eventstamp
		distinct_ips = full_details.values('dstip').distinct()
		# must wait until after distinct query before ordering original queryset:
		#full_details = full_details.order_by('eventstamp')
		for ip in distinct_ips:
			try:
				ip_lookup = IpResolver.objects.filter(ip=ip['dstip'])[0]
				dst_ip = ip_lookup.ip
				location = ip_lookup.location
			except:
				continue
			device_details = full_details.filter(dstip = ip['dstip'])		
			if device_details.count()==0:
				continue
			if(location=="Georgia Tech"):
				priority=1
			else:
				priority=0
			rtt_data.append(cvs_helper.linegraph_normal(device_details,location,1,1,priority,series_id))
		cache_new = JsonCache(deviceid = device, data = json.dumps(rtt_data), datatype = 'rtt', eventstamp = most_recent)
		cache_new.save()
		return

# appends new lmrtt measurements to precomputed (cached) JSON dictionaries for each device. This method updates
# a db record and returns nothing.
def update_lmrtt(device):
	lmrtt_data=[]
	series_id=4
	lmrtt_cache = JsonCache.objects.filter(deviceid=device, datatype='lmrtt')
	if lmrtt_cache.count()!=0:
		latest = lmrtt_cache.latest('eventstamp').eventstamp
		all_records = MLmrtt.objects.filter(deviceid=device,average__lte=3000, eventstamp__gt=latest)
		if (all_records.count()==0):
			return
		uncached_measurements = all_records.order_by('eventstamp')
		latest_record = uncached_measurements.latest('eventstamp')
		# cache is up to date:
		#if latest_record.eventstamp<=lmrtt_cache[0].eventstamp:
			#return
		# uncached_measurements = all_records.filter(eventstamp__gt=lmrtt_cache[0].eventstamp).order_by('eventstamp')
		lmrtt_data = json.loads(lmrtt_cache[0].data)
		lmrtt_data[0]['data'].extend(cvs_helper.linegraph_normal(uncached_measurements,'Last mile latency',1,1,1,series_id)['data'])
		id = lmrtt_cache[0].id
		deviceid = lmrtt_cache[0].deviceid
		update_lmrtt = JsonCache(id=id,deviceid=deviceid,data=json.dumps(lmrtt_data),eventstamp = latest_record.eventstamp, datatype='lmrtt')
		# lmrtt_cache[0].data = json.dumps(lmrtt_data)
		# lmrtt_cache[0].eventstamp = latest_record.eventstamp
		# lmrtt_cache[0].save()
		update_lmrtt.save()
		return
	else:
		all_measurements = MLmrtt.objects.filter(deviceid=device,average__lte=3000)
		# no measurements for this device
		if all_measurements.count()==0:
			return
		latest_measurement = all_measurements.latest('eventstamp').eventstamp
		all_measurements = all_measurements.order_by('eventstamp')
		lmrtt_data.append(cvs_helper.linegraph_normal(all_measurements,'Last mile latency',1,1,1,series_id))
		new_cache = JsonCache(deviceid = device, data = json.dumps(lmrtt_data), datatype = 'lmrtt', eventstamp = latest_measurement)
		new_cache.save()
		return

# appends new capacity measurements to precomputed (cached) JSON dictionaries for each device. This method updates
# a db record and returns nothing.		
def update_capacity(device):
	series_id=5
	# series data for capacity, in json format:
	capacity_data = []
	# retrieve cached data:
	capacity_cache = JsonCache.objects.filter(deviceid=device,datatype='capacity')
	# cacehe not empty:
	if capacity_cache.count()!=0:
		most_recent_cached = capacity_cache.latest('eventstamp').eventstamp
		all_measurements = MCapacity.objects.filter(deviceid=device, eventstamp__gt=most_recent_cached)
		# no new measurements:
		if all_measurements.count()==0:
			return
		most_recent_uncached = all_measurements.latest('eventstamp').eventstamp
		# if most_recent_uncached<=most_recent_cached:
			# cache is up to date
			# return
		capacity_data = json.loads(capacity_cache[0].data)
		capacity_up = capacity_data[0]
		capacity_down = capacity_data[1]
		# retrieve all uncached measurements:
		# uncached_capacity = all_measurements.filter(eventstamp__gt=most_recent_cached)
		uncached_capacity = all_measurements.order_by('eventstamp')
		# if len(uncached_capacity)==0:
			# return
		cap_measure_up = uncached_capacity.filter(direction='up').order_by('eventstamp')
		cap_measure_down = uncached_capacity.filter(direction='dw').order_by('eventstamp')
		capacity_data[0]['data'].extend(cvs_helper.linegraph_normal(cap_measure_up,'Capacity Up',1000,1,0,series_id)['data'])
		capacity_data[1]['data'].extend(cvs_helper.linegraph_normal(cap_measure_down,'Capacity Down',1000,1,0,series_id)['data'])
		id = capacity_cache[0].id
		deviceid = capacity_cache[0].deviceid
		capacity_update = JsonCache(id=id,deviceid=deviceid,data=json.dumps(capacity_data),eventstamp=most_recent_uncached,datatype='capacity')
		# capacity_cache[0].data=json.dumps(capacity_data)
		# capacity_cache[0].eventstamp = most_recent_uncached
		# capacity_cache[0].save()
		capacity_update.save()
	# cache is empty
	else:
		all_capacity= MCapacity.objects.filter(deviceid=device)
		# no measurements:
		if all_capacity.count()==0:
			return
		all_capacity = all_capacity.order_by('eventstamp')
		latest_capacity = all_capacity.latest('eventstamp').eventstamp
		cap_measure_up = all_capacity.filter(direction='up')
		cap_measure_down = all_capacity.filter(direction='dw')
		capacity_data.append(cvs_helper.linegraph_normal(cap_measure_up,'Capacity Up',1000,1,0,series_id))
		capacity_data.append(cvs_helper.linegraph_normal(cap_measure_down,'Capacity Down',1000,1,0,series_id))
		cache_capacity_new = JsonCache(deviceid = device, data =json.dumps(capacity_data), datatype = 'capacity', eventstamp = latest_capacity)
		cache_capacity_new.save()
	return
	
# appends new shaperate measurements to precomputed (cached) JSON dictionaries for each device. This method updates
# a db record and returns nothing.
def update_shaperate(device):
	series_id=5
	# series data for shaperate, in json format:
	shaperate_data = []
	# retrieve cached data:
	shaperate_cache = JsonCache.objects.filter(deviceid=device,datatype='shaperate')
	# cache already contains data:
	if shaperate_cache.count()!=0:
		most_recent_cached = shaperate_cache.latest('eventstamp').eventstamp
		all_measurements = MShaperate.objects.filter(deviceid=device, eventstamp__gt=most_recent_cached)
		if all_measurements.count()==0:
			return
		most_recent_uncached = all_measurements.latest('eventstamp').eventstamp
		# if most_recent_uncached<= most_recent_cached:
			# up to date:
			# return
		shaperate_data = json.loads(shaperate_cache[0].data)
		# split into 4 separate series, upload and download for shaperate and capacity:
		shaperate_up = shaperate_data[0]
		shaperate_down = shaperate_data[1]
		# retrieve all uncached measurements:
		uncached_shaperate = all_measurements.order_by('eventstamp')
		# if len(uncached_shaperate)==0:
			# return
		# separate shaperate records into upload and download
		shape_measure_up = uncached_shaperate.filter(direction='up')
		shape_measure_down = uncached_shaperate.filter(direction='dw')
		# convert records to series data and append to cached data:
		shaperate_data[0]['data'].extend(cvs_helper.linegraph_normal(shape_measure_up,'Shape rate Up',1000,1,0,series_id)['data'])
		shaperate_data[1]['data'].extend(cvs_helper.linegraph_normal(shape_measure_down,'Shape rate Down',1000,1,1,series_id)['data'])
		id = shaperate_cache[0].id
		deviceid = shaperate_cache[0].deviceid
		shaperate_update = JsonCache(id=id,deviceid=deviceid,eventstamp=most_recent_uncached,data=json.dumps(shaperate_data),datatype='shaperate')
		# shaperate_cache[0].data=json.dumps(shaperate_data)
		# shaperate_cache[0].eventstamp = most_recent_uncached
		# shaperate_cache[0].save()
		shaperate_update.save()
	# 1 or both caches are empty:
	else:
		# retrieve all capacity and shaperate measurement records for this device:
		all_shaperate= MShaperate.objects.filter(deviceid=device)
		if all_shaperate.count()==0:
			# no data
			return
		most_recent_cached = all_shaperate.latest('eventstamp').eventstamp
		all_shaperate = all_shaperate.order_by('eventstamp')
		# separate shaperate records into upload and download:
		shape_measure_up = all_shaperate.filter(direction='up')
		shape_measure_down = all_shaperate.filter(direction='dw')
		# convert records into new series to be placed in cache:
		shaperate_data.append(cvs_helper.linegraph_normal(shape_measure_up,'Shape rate Up',1000,1,0,series_id))
		shaperate_data.append(cvs_helper.linegraph_normal(shape_measure_down,'Shape rate Down',1000,1,1,series_id))
		cache_shaperate_new = JsonCache(deviceid = device, data = json.dumps(shaperate_data), datatype = 'shaperate', eventstamp = most_recent_cached)
		cache_shaperate_new.save()
	return	

# appends new underload measurements to precomputed (cached) JSON dictionaries for each device. This method updates
# a db record and returns nothing.
def update_unload(device):
	series_id=6
	# series data in json format:
	unload_data = []
	# retrieve cached data:
	unload_cache = JsonCache.objects.filter(deviceid=device,datatype='unload')
	# cache not empty:
	if unload_cache.count()!=0:
		most_recent_cached = unload_cache.latest('eventstamp').eventstamp
		all_upload = MUlrttup.objects.filter(deviceid=device, eventstamp__gt=most_recent_cached, average__lte=3000)
		all_download = MUlrttdw.objects.filter(deviceid=device, eventstamp__gt=most_recent_cached, average__lte=3000)
		# no measurements:
		if all_upload.count()==0 and all_download.count()==0:
			return
		unload_data = json.loads(unload_cache[0].data)
		#if most_recent_uncached_up<=most_recent_cached and most_recent_uncached_down<=most_recent_cached:
			# cache is up to date
			#return
		if all_upload.count()!=0:
			most_recent_uncached_up = all_upload.latest('eventstamp').eventstamp
			if most_recent_uncached_up>most_recent_cached:
				# retrieve all uncached measurements:
				uncached_up = all_upload.order_by('eventstamp')
				if uncached_up.count()!=0:
					unload_data[1]['data'].extend(cvs_helper.linegraph_normal(uncached_up,'Under Load Up',1,1,0,series_id)['data'])
		if all_download.count()!=0:
			most_recent_uncached_down = all_download.latest('eventstamp').eventstamp
			if most_recent_uncached_down>most_recent_cached:
				# retrieve all uncached measurements:
				uncached_down = all_download.order_by('eventstamp')
				if uncached_down.count()!=0:
					# uncached_down = uncached_down.order_by('eventstamp')
					unload_data[0]['data'].extend(cvs_helper.linegraph_normal(uncached_down,'Under Load Down',1,1,0,series_id)['data'])
		if all_download.count()!=0 and all_upload.count()!=0:
			if most_recent_uncached_down>most_recent_uncached_up:
				most_recent_uncached = most_recent_uncached_down
			else:
				most_recent_uncached = most_recent_uncached_up
		if all_download.count()==0:
			most_recent_uncached = most_recent_uncached_up
		if all_upload.count()==0:
			most_recent_uncached = most_recent_uncached_down
		id = unload_cache[0].id
		deviceid = unload_cache[0].deviceid
		unload_update = JsonCache(id=id,deviceid=deviceid,eventstamp=most_recent_uncached,data=json.dumps(unload_data),datatype='unload')
		# unload_cache[0].data=json.dumps(unload_data)
		# unload_cache[0].eventstamp = most_recent_uncached
		# unload_cache[0].save()
		unload_update.save()
	# cache is empty
	else:
		all_upload = MUlrttup.objects.filter(deviceid=device, average__lte=3000)
		all_download = MUlrttdw.objects.filter(deviceid=device, average__lte=3000)
		# no measurements:
		if all_upload.count()==0 or all_download.count()==0:
			return
		latest_upload = all_upload.latest('eventstamp').eventstamp
		latest_download = all_download.latest('eventstamp').eventstamp
		if latest_upload<latest_download:
			latest_eventstamp = latest_download
		else:
			latest_eventstamp = latest_upload
		all_upload = all_upload.order_by('eventstamp')
		all_download = all_download.order_by('eventstamp')
		unload_data.append(cvs_helper.linegraph_normal(all_download,'Under Load Down',1,1,0,series_id))
		unload_data.append(cvs_helper.linegraph_normal(all_upload,'Under Load Up',1,1,0,series_id))
		cache_unload_new = JsonCache(deviceid = device, data =json.dumps(unload_data), datatype = 'unload', eventstamp = latest_eventstamp)
		cache_unload_new.save()
	return
	

# creates and returns series for average bitrate measurements for devices in a given city:	
def bargraph_compare_bitrate_by_city(city,country,start,end,dir):
	result = []
	params = []
	devices = tuple(views_helper.bargraph_devices_by_city_name(city))
	if len(devices)==0:
		return result
	# parameters for query. Ordering of appending matters:
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	params.append(earliest)
	params.append(latest)
	params.append(dir)
	params.append(devices)
	# start and end dates based on user selection:
	SQL = "SELECT \
		avg(average) AS avg, \
		count(distinct m_bitrate.deviceid) AS count, \
		geoip_isp AS name \
		FROM m_bitrate \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_bitrate.deviceid \
		WHERE m_bitrate.eventstamp>%s AND m_bitrate.eventstamp<%s \
		AND m_bitrate.direction = %s AND m_bitrate.average != 0 \
		AND devicedetails.deviceid IN %s \
		GROUP BY geoip_isp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.bargraph_compare(records, 1000)
	cursor.close()
	return result
	
def bargraph_compare_bitrate_by_country(country,start,end,dir):
	# start and end dates based on user selection:
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	# parameters for query. Ordering of appending matters:
	params = []
	params.append(country)
	params.append(earliest)
	params.append(latest)
	params.append(dir)
	SQL = "SELECT \
		avg(average) AS avg, \
		count(distinct m_bitrate.deviceid) AS count, \
		geoip_isp AS name \
		FROM m_bitrate \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_bitrate.deviceid \
		WHERE geoip_country=%s AND m_bitrate.eventstamp>%s AND m_bitrate.eventstamp<%s \
		AND devicedetails.geoip_isp != 'unknown' AND devicedetails.geoip_isp != '' \
		AND m_bitrate.direction =%s AND m_bitrate.average != 0 \
		GROUP BY geoip_isp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.bargraph_compare(records, 1000)
	return result
	
def bargraph_compare_bitrate_by_isp(isp,start,end,direction,country):
	params = []
	result = []
	devices = tuple(views_helper.bargraph_devices_by_provider_and_country(isp,country))
	if len(devices)==0:
		return result
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	# parameters for query. Ordering of appending matters:
	params.append(earliest)
	params.append(latest)
	params.append(direction)
	params.append(devices)
	# start and end dates based on user selection:
	SQL = "SELECT \
		avg(average) AS avg, \
		count(distinct m_bitrate.deviceid) AS count, \
		geoip_city AS name \
		FROM m_bitrate \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_bitrate.deviceid \
		WHERE m_bitrate.eventstamp>%s AND m_bitrate.eventstamp<%s \
		AND m_bitrate.direction=%s AND m_bitrate.average>0 \
		AND devicedetails.deviceid IN %s \
		GROUP BY geoip_city;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.bargraph_compare(records, 1000)
	cursor.close()
	return result

# creates and returns series for lmrtt measurements for devices in a given city:	
def bargraph_compare_lmrtt_by_city(city,start,end):
	params = []
	result = []
	devices = tuple(views_helper.bargraph_devices_by_city_name(city))
	if len(devices)==0:
		return result
	# start and end dates based on user selection:
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	# parameters for query. Ordering of appending matters:
	params.append(earliest)
	params.append(latest)
	params.append(devices)
	SQL = "SELECT \
		avg(average) AS avg, \
		count(distinct m_lmrtt.deviceid) AS count, \
		geoip_isp AS name \
		FROM m_lmrtt \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_lmrtt.deviceid \
		WHERE m_lmrtt.eventstamp>%s AND m_lmrtt.eventstamp<%s AND m_lmrtt.average<3000 \
		AND devicedetails.deviceid IN %s \
		GROUP BY geoip_isp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.bargraph_compare(records, 1)
	cursor.close()
	return result
	
def bargraph_compare_lmrtt_by_country(country,start,end):
	# start and end dates based on user selection:
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	# parameters for query. Ordering of appending matters:
	params = []
	params.append(country)
	params.append(earliest)
	params.append(latest)
	SQL = "SELECT \
		avg(average) AS avg, \
		count(distinct m_lmrtt.deviceid) AS count, \
		geoip_isp AS name \
		FROM m_lmrtt \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_lmrtt.deviceid \
		WHERE geoip_country=%s AND m_lmrtt.eventstamp>%s AND m_lmrtt.eventstamp<%s AND m_lmrtt.average<3000 \
		GROUP BY geoip_isp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.bargraph_compare(records, 1)
	return result
	
	
def bargraph_compare_lmrtt_by_isp(isp,start,end,country):
	result = []
	params = []
	devices = tuple(views_helper.bargraph_devices_by_provider_and_country(isp,country))
	if len(devices)==0:
		return result
	# start and end dates based on user selection:
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	# parameters for query. Ordering of appending matters:
	params.append(earliest)
	params.append(latest)
	params.append(devices)
	SQL = "SELECT \
		avg(average) AS avg, \
		count(distinct m_lmrtt.deviceid) AS count, \
		geoip_city AS name \
		FROM m_lmrtt \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_lmrtt.deviceid \
		WHERE m_lmrtt.eventstamp>%s AND m_lmrtt.eventstamp<%s AND m_lmrtt.average<3000 \
		AND devicedetails.deviceid IN %s \
		GROUP BY geoip_city;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.bargraph_compare(records, 1)
	cursor.close()
	return result
	
def bargraph_compare_rtt_by_city(city,start,end):
	params = []
	result = []
	devices = tuple(views_helper.bargraph_devices_by_city_name(city))
	if len(devices)==0:
		return result
	dstip = '8.8.8.8'
	# parameters for query. Ordering of appending matters:
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	params.append(earliest)
	params.append(latest)
	params.append(dstip)
	params.append(devices)
	# start and end dates based on user selection:
	SQL = "SELECT \
		avg(average) AS avg, \
		count(distinct m_rtt.deviceid) AS count, \
		geoip_isp AS name \
		FROM m_rtt \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_rtt.deviceid \
		WHERE m_rtt.eventstamp>%s AND m_rtt.eventstamp<%s AND m_rtt.dstip = %s AND m_rtt.average<3000 \
		AND devicedetails.deviceid IN %s \
		GROUP BY geoip_isp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.bargraph_compare(records, 1)
	cursor.close()
	return result
	
def bargraph_compare_rtt_by_country(country,start,end):
	# only measure against a particular server:
	dstip = '8.8.8.8'
	# start and end dates based on user selection:
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	# parameters for query. Ordering of appending matters:
	params = []
	params.append(country)
	params.append(dstip)
	params.append(earliest)
	params.append(latest)
	# start and end dates based on user selection:
	SQL = "SELECT \
		avg(average) AS avg, \
		count(distinct m_rtt.deviceid) AS count, \
		geoip_isp AS name \
		FROM m_rtt \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_rtt.deviceid \
		WHERE geoip_country=%s AND dstip=%s AND m_rtt.eventstamp>%s AND m_rtt.eventstamp<%s AND m_rtt.average<3000 \
		AND devicedetails.geoip_isp != 'unknown' AND devicedetails.geoip_isp != '' \
		GROUP BY geoip_isp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.bargraph_compare(records, 1)
	cursor.close()
	return result
	
def bargraph_compare_rtt_by_isp(isp,start,end,country):
	params = []
	result = []
	# Calculate earliest date of the series based on user selection:
	devices = tuple(views_helper.bargraph_devices_by_provider_and_country(isp,country))
	if len(devices)==0:
		return result
	dstip = '8.8.8.8'
	# start and end dates based on user selection:
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	# parameters for query. Ordering of appending matters:
	params.append(earliest)
	params.append(latest)
	params.append(dstip)
	params.append(devices)
	SQL = "SELECT \
		avg(average) AS avg, \
		count(distinct m_rtt.deviceid) AS count, \
		geoip_city AS name \
		FROM m_rtt \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_rtt.deviceid \
		WHERE m_rtt.eventstamp>%s AND m_rtt.eventstamp<%s AND m_rtt.dstip = %s AND m_rtt.average<3000 \
		AND devicedetails.deviceid IN %s \
		GROUP BY geoip_city;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.bargraph_compare(records, 1)
	cursor.close()
	return result
	
def linegraph_compare_bitrate_by_city(city,country,max_results,start,end,dir):
	params = []
	result = []
	metric = ''
	if dir == 'dw':
		metric = 'bitrate_down'
	else:
		metric = 'bitrate_up'
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	devices = tuple(views_helper.linegraph_devices_by_city_name(city, max_results, earliest, latest, metric))
	if len(devices)==0:
		return result
	params.append(earliest)
	params.append(latest)
	params.append(dir)
	params.append(devices)
	SQL = "SELECT \
		average AS avg, \
		devicedetails.deviceid AS deviceid, \
		geoip_isp AS name, \
		m_bitrate.eventstamp AS eventstamp \
		FROM m_bitrate \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_bitrate.deviceid \
		WHERE m_bitrate.eventstamp>%s AND m_bitrate.eventstamp<%s \
		AND m_bitrate.direction=%s AND m_bitrate.average != 0 \
		AND devicedetails.deviceid IN %s \
		ORDER BY m_bitrate.eventstamp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.linegraph_compare(records, 1000)
	cursor.close()
	return result
	
def linegraph_compare_bitrate_by_isp(isp,max_results,start,end,dir,country):
	params = []
	result = []
	metric = ''
	if dir == 'dw':
		metric = 'bitrate_down'
	else:
		metric = 'bitrate_up'
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	devices = tuple(views_helper.linegraph_devices_by_provider_and_country(isp,country,max_results,earliest,latest,metric))
	if len(devices)==0:
		return result
	params.append(earliest)
	params.append(latest)
	params.append(dir)
	params.append(devices)
	SQL = "SELECT \
		average AS avg, \
		devicedetails.deviceid AS deviceid, \
		geoip_city AS name, \
		m_bitrate.eventstamp AS eventstamp \
		FROM m_bitrate \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_bitrate.deviceid \
		WHERE m_bitrate.eventstamp>%s AND m_bitrate.eventstamp<%s \
		AND m_bitrate.direction=%s AND m_bitrate.average != 0 \
		AND devicedetails.deviceid IN %s \
		ORDER BY m_bitrate.eventstamp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.linegraph_compare(records, 1000)
	cursor.close()
	return result
	
# creates and returns series for lmrtt measurements for devices in a given city:	
def linegraph_compare_lmrtt_by_city(city,max_results,start,end):
	params = []
	result = []
	metric = 'lmrtt'
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	devices = tuple(views_helper.linegraph_devices_by_city_name(city, max_results, earliest, latest, metric))
	if len(devices)==0:
		return result
	params.append(earliest)
	params.append(latest)
	params.append(devices)
	SQL = "SELECT \
		average AS avg, \
		devicedetails.deviceid AS deviceid, \
		geoip_isp AS name, \
		m_lmrtt.eventstamp AS eventstamp \
		FROM m_lmrtt \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_lmrtt.deviceid \
		WHERE m_lmrtt.eventstamp>%s AND m_lmrtt.eventstamp<%s AND m_lmrtt.average<3000 \
		AND devicedetails.deviceid IN %s \
		ORDER BY m_lmrtt.eventstamp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.linegraph_compare(records, 1)
	cursor.close()
	return result
	
def linegraph_compare_lmrtt_by_isp(isp,max_results,start,end,country):
	params = []
	result = []
	metric = 'lmrtt'
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	devices = tuple(views_helper.linegraph_devices_by_provider_and_country(isp,country,max_results,earliest,latest,metric))
	if len(devices)==0:
		return result
	params.append(earliest)
	params.append(latest)
	params.append(devices)
	SQL = "SELECT \
		average AS avg, \
		devicedetails.deviceid AS deviceid, \
		geoip_isp AS name, \
		m_lmrtt.eventstamp AS eventstamp \
		FROM m_lmrtt \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_lmrtt.deviceid \
		WHERE m_lmrtt.eventstamp>%s AND m_lmrtt.eventstamp<%s AND m_lmrtt.average<3000 \
		AND devicedetails.deviceid IN %s \
		ORDER BY m_lmrtt.eventstamp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.linegraph_compare(records, 1)
	cursor.close()
	return result
	
def linegraph_compare_rtt_by_city(city,max_results,start,end):
	params = []
	result = []
	metric = 'rtt'
	dstip = '8.8.8.8'
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	devices = tuple(views_helper.linegraph_devices_by_city_name(city,max_results,earliest,latest,metric))
	if len(devices)==0:
		return result
	params.append(earliest)
	params.append(latest)
	params.append(dstip)
	params.append(devices)
	SQL = "SELECT \
		average AS avg, \
		devicedetails.deviceid AS deviceid, \
		geoip_isp AS name, \
		m_rtt.eventstamp AS eventstamp \
		FROM m_rtt \
		INNER JOIN devicedetails ON devicedetails.deviceid=m_rtt.deviceid \
		WHERE m_rtt.eventstamp>%s AND m_rtt.eventstamp<%s AND m_rtt.dstip=%s \
	    AND m_rtt.average<3000 \
		AND devicedetails.deviceid IN %s \
		ORDER BY m_rtt.eventstamp;"
	cursor = get_dict_cursor()
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	result = cvs_helper.linegraph_compare(records, 1)
	cursor.close()
	return result
	
def linegraph_compare_rtt_by_isp(isp,max_results,start,end,country):
	series = []
	result = []
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	devices = Devicedetails.objects.filter(isp=isp,eventstamp__lte=latest)
	if len(devices)==0:
		return result
	for d in devices:
		parse = parse_rtt_compare(d.deviceid,earliest,latest)
		result.append(dict(name=d.city + ' Device', type='line', data=parse))
	return result
	
# returns a single series:
def parse_rtt_compare_by_isp(device,earliest,latest,city):
	data = []
	dstip = '8.8.8.8'
	city = ''
	filename = settings.PROJECT_ROOT + '/summary/measurements/' + device
	# garbage characters to be removed:
	remove = ')("\n'
	f = open(filename, 'r')
	# file is closed automatically after all lines are read:
	with open(filename,'r') as f:
		# each line represents one measurement record:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split(',')
			# eventstamp:
			entry.append(int(record[0]))
			# average:
			entry.append(float(record[1]))
			data.append(entry)
	# order measurements by eventstamp:
	sorted_data = sorted(data, key=lambda x: x[0])
	# apply filtering:
	sorted_data = [(x,y) for x,y,z in sorted_data if x>earliest and x<latest and z==dstip]
	series = dict(name=city, type='line', data=sorted_data)
	return series

# returns multiple series for the same device:	
def parse_rtt_measurements(device):
	result = []
	data = []
	dstips = []
	filename = settings.PROJECT_ROOT + '/summary/measurements/' + device
	# garbage characters to be removed:
	remove = ')("\n'
	ipr = IpResolver.objects.all()
	f = open(filename, 'r')
	with open(filename,'r') as f:
		# each line represents one measurement record:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split(',')
			# eventstamp:
			entry.append(int(record[0]))
			# average:
			entry.append(float(record[1]))
			# mserver address:
			dstip = record[2]
			entry.append(dstip)
			if dstip not in dstips and dstip!='':
				dstips.append(dstip)
			data.append(entry)
	f.close()
	# sort by eventstamp:
	sorted_data = sorted(data, key=lambda x: x[0])
	# group data into sub-series by measurement server
	for dstip in dstips:
		mserver = ipr.filter(ip=dstip)
		if len(mserver)==0:
			continue
		# measurements (eventstamp,avg) are grouped by dstip, though dstip itself is discarded:
		series_data = [(x,y) for x,y,z in sorted_data if  z==dstip]
		series = dict(name=mserver.location,type='line',data=series_data)
		result.append(series)
	return result
	
def get_measurement_server_name(dstip):
	ipr = IpResolver.objects.filter(ip=dstip)
	if len(ipr)!=0:
		return ipr[0].location 
	return ''
	
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
	
# creates and sets a hashkey for a device
def assign_hash(device):
	dev = Devicedetails.objects.get(deviceid=device)
	hash = hashlib.md5()
	hash.update(dev.deviceid)
	hash = hash.hexdigest()
	dev.hashkey = hash
	dev.save()
	# devicedetails entry for this device does not exist:
	return
	
# calls assign_hash for every device without a hashkey
def assign_hashkeys():
	unhashed_devices = Devicedetails.objects.filter(hashkey='')
	if unhashed_devices.count()!=0:
		for dev in unhashed_devices:
			assign_hash(dev.deviceid)
	return
		
	


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

def device_count_and_country_data():
	distinct_countries = list_countries()
	response = []
	for country in distinct_countries:
		if country!='':
			value={}
			count = device_count_for_country(country)
			value['country']=country
			value['count']=count
			response.append(value) 
	return response
	
def get_isp_count():
	distinct_isps = list_isps()
	response = []
	for isp in distinct_isps:
		if isp!='':
			value={}
			count = device_count_for_isp(isp)
			value['isp']=isp
			value['count']=count
			response.append(value) 
	return response

def device_count_for_country(cntry):
    return Devicedetails.objects.filter(country=cntry).count()
	
def device_count_for_isp(provider):
    return Devicedetails.objects.filter(isp=provider).count()
    

def list_countries():
    ret=[]
    out = Devicedetails.objects.values('country').distinct()
    for one in out:
        value = ast.literal_eval(str(one))
        v = value['country']
        ret.append(v)
    ret.sort()
    return ret
	
def list_isps():
    ret=[]
    out = Devicedetails.objects.values('isp').distinct()
    for one in out:
        value = ast.literal_eval(str(one))
        v = value['isp']
        ret.append(v)
    ret.sort()
    return ret

def get_num_common_locations(device_details):
    return Devicedetails.objects.filter(city=device_details.city).count()-1

def get_num_common_providers(device_details):
    return Devicedetails.objects.filter(isp=device_details.isp).count()-1

def get_num_devices(device_details):
    return Devicedetails.objects.exclude(deviceid=device_details.deviceid).count()-1

def get_first_measurement(device):
	try:
		first = MBitrate.objects.filter(deviceid=device).order_by('eventstamp')[0:3]    
		return first[0].eventstamp.strftime("%B %d, %Y")
	except:
		return None

def get_last_measurement(device):
	try:
		last = MBitrate.objects.filter(deviceid=device).order_by('-eventstamp')[0:3]
		return last[0].eventstamp.strftime("%B %d, %Y")
	except:
		return None
	
def get_latest_download(device):
	latest = MBitrate.objects.filter(deviceid=device).order_by('-eventstamp')
	latest = latest.filter(dstip = '143.215.131.173')
	ret = {}
	try:
		ret['average']= latest[0].average
		ret['eventstamp']= latest[0].eventstamp.strftime("%B %d, %Y, %I:%M %p")
	except:
		return ret
	return ret

def get_latest_upload(device):
	latest = MBitrate.objects.filter(deviceid=device).order_by('-eventstamp')
	latest = latest.filter(srcip = '143.215.131.173')
	ret = {}
	try:
		ret['average']= latest[0].average
		ret['eventstamp']= latest[0].eventstamp.strftime("%B %d, %Y, %I:%M %p")
	except:
		return ret
	return ret

def get_latest_lastmile(device):
	latest = MLmrtt.objects.filter(deviceid=device,average__lte=3000).order_by('-eventstamp')
	ret = {}
	try:
		ret['average']= latest[0].average
		ret['eventstamp']= latest[0].eventstamp.strftime("%B %d, %Y, %I:%M %p")
	except:
		return ret
	return ret

def get_latest_roundtrip(device):
	latest = MRtt.objects.filter(deviceid=device,average__lte=3000).order_by('-eventstamp')	
	ret = {}
	try:
		ret['average']= latest[0].average
		ret['eventstamp']= latest[0].eventstamp.strftime("%B %d, %Y, %I:%M %p")
	except:
		return ret
	return ret
	
def get_latest_shaperate(device):
	latest = MShaperate.objects.filter(deviceid=device,average__lte=300).order_by('-eventstamp')
	ret = {}
	try:
		ret['average']= latest[0].average
		ret['eventstamp']= latest[0].eventstamp.strftime("%B %d, %Y, %I:%M %p")
	except:
		return ret
	return ret


def get_location(device):
    device = device.replace(':','')
    details = Devicedetails.objects.filter(deviceid=device)
    if details.count()>0:
        return (details[0].city + ", " + details[0].country)

    dev = MBitrate.objects.filter(deviceid=device, srcip ='8.8.8.8' )
    if dev.count()>0:
        ip = str(dev[0].dstip)
        urlobj=urllib2.urlopen("http://api.ipinfodb.com/v3/ip-city/?key=c91c266accebc12bc7bbdd7fef4b5055c1485208bb6c20b4cc2991e67a3e3d34&ip=" + ip + "&format=json")
        r1 = urlobj.read()
        urlobj.close()
        datadict = json.loads(r1)
        res = datadict["cityName"] + "," + datadict["countryName"]
        return (res)  
    
    return ('unavailable')

def get_google_maps_result_from_request(address):
    params = urllib.urlencode({'key': 'AIzaSyBHEmkA7XyusAjA9Zf-UnLSR9ydvCExY6k', 'output': 'json', 'q': str(address)})
    f = urllib2.urlopen("http://maps.google.com/maps/geo?"+str(params))
    result = ast.literal_eval(f.read())
    return result

def save_device_details_from_request(request,device):
	hashing = views_helper.get_hash(device)
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

	try:
		address = dcity+","+dstate+","+dcountry
		result = get_google_maps_result_from_request(str(address))
		if result['Status']['code'] == 200:
   
		    coord=result['Placemark'][0]['Point']['coordinates']
		    details.latitude = coord[1]
		    details.longitude=coord[0]
		    details.country=result['Placemark'][0]['AddressDetails']['Country']['CountryName']
		    details.state=result['Placemark'][0]['AddressDetails']['Country']['AdministrativeArea']['AdministrativeAreaName']
		    details.city=result['Placemark'][0]['AddressDetails']['Country']['AdministrativeArea']['Locality']['LocalityName']
	except Exception as inst:
		print type(inst)
		print inst
       
	details.is_default=False
	details.save()

# creates a new devicedetails entry. returns True on success
def save_device_details_from_default(device):
	# check if this is a valid mac address
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

def deviceid_to_nodeid(device):
    return "OW" + device.upper()

def get_dict_cursor():
    conn_string = "host='" + settings.DATABASES['default']['HOST'] + \
                   "' dbname='" + settings.DATABASES['default']['NAME'] + \
                   "' user='" + settings.DATABASES['default']['USER'] + \
                   "' password='" + settings.DATABASES['default']['PASSWORD'] + "'";
                   
    conn = psycopg2.connect(conn_string)
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	
