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

#returns a line series representing RTT measurements for a given device, in a given timeframe:	
def parse_rtt_compare(device,earliest,latest,name):
	data = []
	#only want measurements against a particular measurement server:
	dstip = '8.8.8.8'
	earliest = datetime_helper.datetime_to_JSON(earliest)
	latest = datetime_helper.datetime_to_JSON(latest)
	device = device.replace(':','')
	filename = settings.PROJECT_ROOT + '/summary/measurements/rtt/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	#file is closed automatically after all lines are read:
	with open(filename,'r') as f:
		#each line represents one measurement record:
		for record in f:
			entry = []
			try:
				for i in range(0,len(remove)):
					record = record.replace(remove[i],'')
				record = record.split('|')
				#eventstamp:
				entry.append(int(record[0]))
				#average:
				entry.append(float(record[1]))
				#dstip:
				entry.append(record[2])
				data.append(entry)
			except:
				continue
	#apply filtering:
	data = [(x,y,z) for x,y,z in data if (x>earliest and x<latest and z==dstip)]
	data = sorted(data, key=lambda x: x[0])
	series = dict(name=name + ' device', type='line',data=data)
	return series

#returns a line series representing LMRTT measurements for a given device, in a given timeframe:	
def parse_lmrtt_compare(device,earliest,latest,name):	
	data = []
	earliest = datetime_helper.datetime_to_JSON(earliest)
	latest = datetime_helper.datetime_to_JSON(latest)
	device = device.replace(':','')
	filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	#file is closed automatically after all lines are read:
	with open(filename,'r') as f:
		#each line represents one measurement record:
		for record in f:
			entry = []
			try:
				for i in range(0,len(remove)):
					record = record.replace(remove[i],'')
				record = record.split('|')
				#eventstamp:
				entry.append(int(record[0]))
				#average:
				entry.append(float(record[1]))
				data.append(entry)
			except:
				continue
	#apply filtering:
	data = [(x,y) for x,y in data if (x>earliest and x<latest)]
	data = sorted(data, key=lambda x: x[0])
	series = dict(name=name + ' device', type='line',data=data)
	return series

#returns multiple bar series representing average bitrate measurements for devices in a given city,
#in a given timeframe:
def parse_bitrate_city_average(start_date,end_date,city,direction):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = Devicedetails.objects.values('geoip_isp').distinct()
	filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate_averages/city'
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#average (a):
			entry.append(float(record[0])*1000)
			#measurement count (b):
			entry.append(int(record[1]))
			#day (c)
			entry.append(int(record[2]))
			#city (d)
			entry.append(record[3])
			#device count (e):
			entry.append(record[4])
			#direction (f):
			entry.append(record[5])
			#isp (g):
			entry.append(record[6])
			data.append(entry)
	f.close()
	for isp in isps:
		provider = isp['geoip_isp']
		if provider==None or provider=='':
			continue
		for i in range(0,len(remove)):
				provider = provider.replace(remove[i],'')
		filtered = [(a,b,c,d,e,f,g) for a,b,c,d,e,f,g in data if d==city and c>start and c<end and g==provider and f==direction]
		if len(filtered)==0:
			continue
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		#total number of measurements:
		n_measurements = sum(x[1] for x in filtered)
		#apply weight to each average based on total number of measurements, and sum to get the overall average:
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		series = dict(name=provider, type='bar', data=average, count=d_count)
		ret.append(series)
	return ret
	
#returns multiple bar series representing average bitrate measurements for devices in a given country,
#in a given timeframe:
def parse_bitrate_country_average(start_date,end_date,country,direction):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = Devicedetails.objects.values('geoip_isp').distinct()
	filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate_averages/country'
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#average (a):
			entry.append(float(record[0])*1000)
			#measurement count (b):
			entry.append(int(record[1]))
			#day (c)
			entry.append(int(record[2]))
			#country (d)
			entry.append(record[3])
			#device count (e):
			entry.append(record[4])
			#direction (f):
			entry.append(record[5])
			#isp (g):
			entry.append(record[6])
			data.append(entry)
	f.close()
	for isp in isps:
		provider = isp['geoip_isp']
		if provider==None or provider=='':
			continue
		for i in range(0,len(remove)):
				provider = provider.replace(remove[i],'')
		filtered = [(a,b,c,d,e,f,g) for a,b,c,d,e,f,g in data if d==country and c>start and c<end and g==provider and f==direction]
		if len(filtered)==0:
			continue
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		#total number of measurements:
		n_measurements = sum(x[1] for x in filtered)
		#apply weight to each average based on total number of measurements, and sum to get the overall average:
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		series = dict(name=provider, type='bar', data=average, count=d_count)
		ret.append(series)
	return ret
	
#returns multiple bar series representing average bitrate measurements for devices under a given isp,
#in a given timeframe:
def parse_bitrate_isp_average(start_date,end_date,isp,direction,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	cities = Devicedetails.objects.values('geoip_city').distinct()
	filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate_averages/isp'
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#average (a):
			entry.append(float(record[0])*1000)
			#measurement count (b):
			entry.append(int(record[1]))
			#day (c)
			entry.append(int(record[2]))
			#isp (d)
			entry.append(record[3])
			#device count (e):
			entry.append(record[4])
			#direction (f):
			entry.append(record[5])
			#country(g):
			entry.append(record[6])
			#city(h)
			entry.append(record[7])
			data.append(entry)
	f.close()
	for city in cities:
		city_name = city['geoip_city']
		if city_name==None or city_name=='':
			continue
		for i in range(0,len(remove)):
				city_name = city_name.replace(remove[i],'')
		filtered = []
		if country=="none":
			filtered = [(a,b,c,d,e,f,g,h) for a,b,c,d,e,f,g,h in data if d==isp and c>start and c<end and h==city_name and f==direction]
		else:
			filtered = [(a,b,c,d,e,f,g,h) for a,b,c,d,e,f,g,h in data if d==isp and c>start and c<end and h==city_name and f==direction and g==country]
		if len(filtered)==0:
			continue
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		#total number of measurements:
		n_measurements = sum(x[1] for x in filtered)
		#apply weight to each average based on total number of measurements, and sum to get the overall average:
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		series = dict(name=city_name, type='bar', data=average, count=d_count)
		ret.append(series)
	return ret
	
#returns multiple bar series representing average LMRTT measurements for devices in a given city,
#in a given timeframe:
def parse_lmrtt_city_average(start_date,end_date,city):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = Devicedetails.objects.values('geoip_isp').distinct()
	filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt_averages/city'
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#average (a):
			entry.append(float(record[0]))
			#measurement count (b):
			entry.append(int(record[1]))
			#day (c)
			entry.append(int(record[2]))
			#city (d)
			entry.append(record[3])
			#device count (e):
			entry.append(record[4])
			#isp (f):
			entry.append(record[5])
			data.append(entry)
	f.close()
	for isp in isps:
		provider = isp['geoip_isp']
		if provider==None or provider=='':
			continue
		for i in range(0,len(remove)):
				provider = provider.replace(remove[i],'')
		filtered = [(a,b,c,d,e,f) for a,b,c,d,e,f in data if d==city and c>start and c<end and f==provider]
		if len(filtered)==0:
			continue
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		#total number of measurements:
		n_measurements = sum(x[1] for x in filtered)
		#apply weight to each average based on total number of measurements, and sum to get the overall average:
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		series = dict(name=provider, type='bar', data=average, count=d_count)
		ret.append(series)
	return ret
	
#returns multiple bar series representing average LMRTT measurements for devices in a given country,
#in a given timeframe:
def parse_lmrtt_country_average(start_date,end_date,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = Devicedetails.objects.values('geoip_isp').distinct()
	filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt_averages/country'
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#average (a):
			entry.append(float(record[0]))
			#measurement count (b):
			entry.append(int(record[1]))
			#day (c)
			entry.append(int(record[2]))
			#country (d)
			entry.append(record[3])
			#device count (e):
			entry.append(record[4])
			#isp (f):
			entry.append(record[5])
			data.append(entry)
	f.close()
	for isp in isps:
		provider = isp['geoip_isp']
		if provider==None or provider=='':
			continue
		for i in range(0,len(remove)):
				provider = provider.replace(remove[i],'')
		filtered = [(a,b,c,d,e,f) for a,b,c,d,e,f in data if d==country and c>start and c<end and f==provider]
		if len(filtered)==0:
			continue
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		#total number of measurements:
		n_measurements = sum(x[1] for x in filtered)
		#apply weight to each average based on total number of measurements, and sum to get the overall average:
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		series = dict(name=provider, type='bar', data=average, count=d_count)
		ret.append(series)
	return ret

#returns multiple bar series representing average LMRTT measurements for devices under a given ISP,
#in a given timeframe:
def parse_lmrtt_isp_average(start_date,end_date,isp,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	cities = Devicedetails.objects.values('geoip_city').distinct()
	filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt_averages/isp'
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#average (a):
			entry.append(float(record[0]))
			#measurement count (b):
			entry.append(int(record[1]))
			#day (c)
			entry.append(int(record[2]))
			#isp (d)
			entry.append(record[3])
			#device count (e):
			entry.append(record[4])
			#country(f):
			entry.append(record[5])
			#city(g)
			entry.append(record[6])
			data.append(entry)
	f.close()
	for city in cities:
		city_name = city['geoip_city']
		if city_name==None or city_name=='':
			continue
		for i in range(0,len(remove)):
				city_name = city_name.replace(remove[i],'')
		filtered = []
		if country=="none":
			filtered = [(a,b,c,d,e,f,g) for a,b,c,d,e,f,g in data if d==isp and c>start and c<end and g==city_name]
		else:
			filtered = [(a,b,c,d,e,f,g) for a,b,c,d,e,f,g in data if d==isp and c>start and c<end and g==city_name and f==country]
		if len(filtered)==0:
			continue
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		#total number of measurements:
		n_measurements = sum(x[1] for x in filtered)
		#apply weight to each average based on total number of measurements, and sum to get the overall average:
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		series = dict(name=city_name, type='bar', data=average, count=d_count)
		ret.append(series)
	return ret
	
#returns multiple bar series representing average RTT measurements for devices in a given city,
#in a given timeframe:
def parse_rtt_city_average(start_date,end_date,city):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = Devicedetails.objects.values('geoip_isp').distinct()
	filename = settings.PROJECT_ROOT + '/summary/measurements/rtt_averages/city'
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#average (a):
			entry.append(float(record[0]))
			#measurement count (b):
			entry.append(int(record[1]))
			#day (c)
			entry.append(int(record[2]))
			#city (d)
			entry.append(record[3])
			#device count (e):
			entry.append(record[4])
			#isp (f):
			entry.append(record[5])
			data.append(entry)
	f.close()
	for isp in isps:
		provider = isp['geoip_isp']
		if provider==None or provider=='':
			continue
		for i in range(0,len(remove)):
				provider = provider.replace(remove[i],'')
		filtered = [(a,b,c,d,e,f) for a,b,c,d,e,f in data if d==city and c>start and c<end and f==provider]
		if len(filtered)==0:
			continue
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		#total number of measurements:
		n_measurements = sum(x[1] for x in filtered)
		#apply weight to each average based on total number of measurements, and sum to get the overall average:
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		series = dict(name=provider, type='bar', data=average, count=d_count)
		ret.append(series)
	return ret
	
#returns multiple bar series representing average RTT measurements for devices in a given country,
#in a given timeframe:
def parse_rtt_country_average(start_date,end_date,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = Devicedetails.objects.values('geoip_isp').distinct()
	filename = settings.PROJECT_ROOT + '/summary/measurements/rtt_averages/country'
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#average (a):
			entry.append(float(record[0]))
			#measurement count (b):
			entry.append(int(record[1]))
			#day (c)
			entry.append(int(record[2]))
			#country (d)
			entry.append(record[3])
			#device count (e):
			entry.append(record[4])
			#isp (f):
			entry.append(record[5])
			data.append(entry)
	f.close()
	for isp in isps:
		provider = isp['geoip_isp']
		if provider==None or provider=='':
			continue
		for i in range(0,len(remove)):
				provider = provider.replace(remove[i],'')
		filtered = [(a,b,c,d,e,f) for a,b,c,d,e,f in data if d==country and c>start and c<end and f==provider]
		if len(filtered)==0:
			continue
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		#total number of measurements:
		n_measurements = sum(x[1] for x in filtered)
		#apply weight to each average based on total number of measurements, and sum to get the overall average:
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		series = dict(name=provider, type='bar', data=average, count=d_count)
		ret.append(series)
	return ret
	
#returns multiple bar series representing average RTT measurements for devices under a given ISP,
#in a given timeframe:
def parse_rtt_isp_average(start_date,end_date,isp,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	cities = Devicedetails.objects.values('geoip_city').distinct()
	filename = settings.PROJECT_ROOT + '/summary/measurements/rtt_averages/isp'
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#average (a):
			entry.append(float(record[0]))
			#measurement count (b):
			entry.append(int(record[1]))
			#day (c)
			entry.append(int(record[2]))
			#isp (d)
			entry.append(record[3])
			#device count (e):
			entry.append(record[4])
			#country(f):
			entry.append(record[5])
			#city(g)
			entry.append(record[6])
			data.append(entry)
	f.close()
	for city in cities:
		city_name = city['geoip_city']
		if city_name==None or city_name=='':
			continue
		for i in range(0,len(remove)):
				city_name = city_name.replace(remove[i],'')
		filtered = []
		if country=="none":
			filtered = [(a,b,c,d,e,f,g) for a,b,c,d,e,f,g in data if d==isp and c>start and c<end and g==city_name]
		else:
			filtered = [(a,b,c,d,e,f,g) for a,b,c,d,e,f,g in data if d==isp and c>start and c<end and g==city_name and f==country]
		if len(filtered)==0:
			continue
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		#total number of measurements:
		n_measurements = sum(x[1] for x in filtered)
		#apply weight to each average based on total number of measurements, and sum to get the overall average:
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		series = dict(name=city_name, type='bar', data=average, count=d_count)
		ret.append(series)
	return ret	

#returns a single line series representing bitrate measurements for a given device in a given timeframe:	
def parse_bitrate_compare(device,earliest,latest,dir,name):
	data = []
	earliest = datetime_helper.datetime_to_JSON(earliest)
	latest = datetime_helper.datetime_to_JSON(latest)
	device = device.replace(':','')
	filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	#file is closed automatically after all lines are read:
	with open(filename,'r') as f:
		#each line represents one measurement record:
		for record in f:
			entry = []
			try:
				for i in range(0,len(remove)):
					record = record.replace(remove[i],'')
				record = record.split('|')
				#eventstamp:
				entry.append(int(record[0]))
				#average:
				entry.append(float(record[1])*1000)
				#direction:
				entry.append(record[2])
				#toolid:
				entry.append(record[3])
				data.append(entry)
			except:
				continue
	data = sorted(data, key=lambda x: x[0])
	#apply filtering:
	data = [(x,y) for x,y,z,t in data if (x>earliest and x<latest and z==dir and t=='NETPERF_3')]
	series = dict(name=name + ' device', type='line',data=data)
	return series	
		
#returns line series representing all bitrate measurements for a given device:	
def parse_bitrate_measurements(device, dir):
	result = []
	data = []
	device = device.replace(':','')
	filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	with open(filename,'r') as f:
		#each line represents one measurement record:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#eventstamp:
			entry.append(int(record[0]))
			#average:
			entry.append(float(record[1])*1000)
			#direction:
			direction = record[2]
			entry.append(direction)
			toolid = record[3]
			entry.append(toolid)
			data.append(entry)
	#sort by eventstamp:
	sorted_data = sorted(data, key=lambda x: x[0])
	sorted_multi = [(x,y) for x,y,z,t in sorted_data if z==dir and t=='NETPERF_3']
	sorted_single = [(x,y) for x,y,z,t in sorted_data if z==dir and t!='NETPERF_3']
	multi_series = dict(name='Multi-threaded TCP', type='line',data=sorted_multi,priority=1)
	if dir=='dw':
		multi_series['id']=1
	else:
		multi_series['id']=2
	single_series = dict(name='Single-threaded TCP', type='line', data=sorted_single)
	result.append(multi_series)
	result.append(single_series)
	return result
	
#returns line series representing all underload measurements for a given device:	
def parse_underload_measurements(device):
	result = []
	data = []
	filename = settings.PROJECT_ROOT + '/summary/measurements/underload/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	f = open(filename, 'r')
	with open(filename,'r') as f:
		#each line represents one measurement record:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#eventstamp:
			entry.append(int(record[0]))
			#average:
			entry.append(float(record[1]))
			#direction:
			direction = record[2]
			entry.append(direction)
			data.append(entry)
	#sort by eventstamp:
	sorted_data = sorted(data, key=lambda x: x[0])
	sorted_up = [(x,y) for x,y,z in sorted_data if z=='up']
	sorted_dw = [(x,y) for x,y,z in sorted_data if z=='dw']
	series_up = dict(name='Under Load Up', type='line',data=sorted_up)
	series_dw = dict(name='Under Load Down', type='line', data=sorted_dw)
	result.append(series_up)
	result.append(series_dw)
	return result

#returns line series representing all RTT measurements for a given device:	
def parse_rtt_measurements(device):
	result = []
	data = []
	dstips = []
	filename = settings.PROJECT_ROOT + '/summary/measurements/rtt/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	ipr = IpResolver.objects.all()
	f = open(filename, 'r')
	with open(filename,'r') as f:
		#each line represents one measurement record:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#eventstamp:
			entry.append(int(record[0]))
			#average:
			entry.append(float(record[1]))
			#mserver address:
			dstip = record[2]
			entry.append(dstip)
			if dstip not in dstips and dstip!='':
				dstips.append(dstip)
			data.append(entry)
	f.close()
	#sort by eventstamp:
	sorted_data = sorted(data, key=lambda x: x[0])
	#group data into sub-series by measurement server
	for dstip in dstips:
		mserver = ipr.filter(ip=dstip)
		if len(mserver)==0:
			continue
		#measurements are grouped by dstip, though dstip itself is discarded:
		series_data = [(x,y) for x,y,z in sorted_data if  z==dstip]
		series = dict(name=mserver[0].location,type='line',data=series_data)
		result.append(series)
	return result
	
#returns line series representing all LMRTT measurements for a given device:	
def parse_lmrtt_measurements(device):
	data = []
	result = []
	filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	f = open(filename, 'r')
	with open(filename,'r') as f:
		#each line represents one measurement record:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#eventstamp:
			entry.append(int(record[0]))
			#average:
			entry.append(float(record[1]))
			data.append(entry)
	f.close()
	#sort by eventstamp:
	sorted_data = sorted(data, key=lambda x: x[0])
	series = dict(name='Last mile latency', type='line', data=sorted_data, priority=1, id=4)
	result.append(series)
	return result
	
#returns line series representing all shaperate measurements for a given device:	
def parse_shaperate_measurements(device):
	data = []
	result = []
	filename = settings.PROJECT_ROOT + '/summary/measurements/shaperate/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	f = open(filename, 'r')
	with open(filename,'r') as f:
		#each line represents one measurement record:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#eventstamp:
			entry.append(int(record[0]))
			#average:
			entry.append(float(record[1])*1000)
			#direction:
			entry.append(record[2])
			data.append(entry)
	f.close()
	#sort by eventstamp:
	sorted_data = sorted(data, key=lambda x: x[0])
	sorted_up = [(x,y) for x,y,z in sorted_data if  z=='up']
	sorted_down = [(x,y) for x,y,z in sorted_data if  z=='dw']
	series_up = dict(name='Shaperate Up', type='line', data=sorted_up)
	series_down = dict(name='Shaperate Down', type='line', data=sorted_down, priority=1, id=5)
	result.append(series_up)
	result.append(series_down)
	return result
	
#returns line series representing all capacity measurements for a given device:	
def parse_capacity_measurements(device):
	data = []
	result = []
	filename = settings.PROJECT_ROOT + '/summary/measurements/capacity/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	f = open(filename, 'r')
	with open(filename,'r') as f:
		#each line represents one measurement record:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			#eventstamp:
			entry.append(int(record[0]))
			#average:
			entry.append(float(record[1])*1000)
			#direction:
			entry.append(record[2])
			data.append(entry)
	f.close()
	#sort by eventstamp:
	sorted_data = sorted(data, key=lambda x: x[0])
	sorted_up = [(x,y) for x,y,z in sorted_data if  z=='up']
	sorted_down = [(x,y) for x,y,z in sorted_data if  z=='dw']
	series_up = dict(name='Capacity Up', type='line', data=sorted_up)
	series_down = dict(name='Capacity Down', type='line', data=sorted_down)
	result.append(series_up)
	result.append(series_down)
	return result

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
	
#creates and sets a hashkey for a single device:
def assign_hash(device):
	dev = Devicedetails.objects.get(deviceid=device)
	hash = hashlib.md5()
	hash.update(dev.deviceid)
	hash = hash.hexdigest()
	dev.hashkey = hash
	dev.save()
	return
	
#calls assign_hash for every device without a hashkey:
def assign_hashkeys():
	unhashed_devices = Devicedetails.objects.filter(hashkey='')
	if unhashed_devices.count()!=0:
		for dev in unhashed_devices:
			assign_hash(dev.deviceid)
	return

#gets the date of the oldest bitrate measurement for a device:
def get_first_measurement(device):
	try:
		first = MBitrate.objects.filter(deviceid=device).order_by('eventstamp')[0:1]    
		return first[0].eventstamp.strftime("%B %d, %Y")
	except:
		return None

#gets the data of the most recent mbitrate measurement for a device:
def get_last_measurement(device):
	try:
		last = MBitrate.objects.filter(deviceid=device).order_by('-eventstamp')[0:1]
		return last[0].eventstamp.strftime("%B %d, %Y")
	except:
		return None

#gets the location of the device. This is the location as specified by the user, as opposed to
#resolved from IP:
def get_location(device):
    device = device.replace(':','')
    details = Devicedetails.objects.filter(deviceid=device)
    if details.count()>0:
        return (details[0].city + ", " + details[0].country)  
    return "unavailable"

#modifies a devicedetails record with the values set on the edit device page:
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
		
