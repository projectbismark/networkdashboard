from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
import random
from datetime import datetime, timedelta
from time import time,mktime,strftime
import hashlib,httplib,urllib2
import cvs_helper,datetime_helper,geoip_helper, views_helper, database_helper
import ast
import psycopg2
import psycopg2.extras
from django.conf import settings

#returns RTT averages for each country for the given measurement server and daterange
def parse_countries_vis_data(start,end,server):
	countries = database_helper.get_device_countries()
	data = []
	ret = []
	filename = settings.PROJECT_ROOT + '/summary/measurements/server_averages/' + server
	# garbage characters to be removed:
	remove = ')("\n '
	with open(filename,'r') as f:
		# each line represents one measurement record:
		for record in f:
			entry = []
			for i in range(0,len(remove)):
				record = record.replace(remove[i],'')
			record = record.split('|')
			# average:
			entry.append(float(record[0]))
			# measurement count:
			entry.append(float(record[1]))
			# day
			entry.append(int(record[2]))
			# country
			entry.append(record[3])
			# device count:
			entry.append(record[4])
			data.append(entry)
	f.close()
	for c in countries:
		cc = c['country_code']
		if cc==None or cc=='':
			continue
		for i in range(0,len(remove)):
				cc = cc.replace(remove[i],'')
		filtered = [(x,y,z,r,s) for x,y,z,r,s in data if r==cc and z>start and z<end]
		try:
			d_count = max(x[4] for x in filtered)
		except:
			continue
		n_measurements = sum(x[1] for x in filtered)
		average = sum((x[0]*x[1]/n_measurements) for x in filtered)
		entry=[]
		entry.append(cc)
		entry.append(d_count)
		entry.append(n_measurements)
		entry.append(average)
		ret.append(entry)
	return ret

#parse coordinates from file for device map: 
def parse_coords():
	coord_data = []
	filename = settings.PROJECT_ROOT + '/summary/measurements/map/coord_data'
	with open(filename,'r') as f:
		for line in f:
			entry = {}
			line = line.replace('\n','')
			line = line.split('|')
			entry['hash'] = line[0]
			entry['lat'] = line[1]
			entry['lon'] = line[2]
			entry['isp'] = line[3]
			entry['active'] = line[4]
			entry['server'] = line[5]
			coord_data.append(entry)
	return coord_data

#returns total number of devices with recent measurements:
def get_active_count():
	active_count = 0
	filename = settings.PROJECT_ROOT + '/summary/device_data/devices'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			#the flag for recently active, set according to threshold defined in update_static_content:
			latest = int(line[5])
			if latest:
				active_count += 1
	return active_count

#returns total number of devices:	
def get_device_count():
	device_count = 0
	filename = settings.PROJECT_ROOT + '/summary/device_data/devices'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			city = line[2]
			country = line[3]
			isp = line[4]
			#to be considered valid, a device's ISP, country, or city must be resolvable from its IP:
			if ((city!=None and city!='') or (country!=None and country!='') or (isp!=None and isp!='')):
				device_count+=1
	return device_count

#returns list of dictionaries containing counts for total and active devices for each isp:
def get_isp_data():
	isp_list = []
	filename = settings.PROJECT_ROOT + '/summary/device_data/isp_count'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			if len(line)!=3:
				continue
			isp = line[0]
			count = line[1]
			active_count = line[2]
			value = {}
			value['isp'] = isp.lstrip()
			value['count'] = count
			value['count_active'] = active_count
			isp_list.append(value)
	return isp_list

#returns list of dictionaries containing counts for total and active devices for each city:
def get_city_data():
	city_list = []
	filename = settings.PROJECT_ROOT + '/summary/device_data/city_count'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			if len(line)!=4:
				continue
			city = line[0]
			country = line[1]
			count = line[2]
			active_count = line[3]
			value = {}
			value['city'] = city
			value['country'] = country
			value['count'] = count
			value['count_active'] = active_count
			city_list.append(value)
	return city_list

#returns list of dictionaries containing counts for total and active devices for each country:
def get_country_data():
	country_list = []
	filename = settings.PROJECT_ROOT + '/summary/device_data/country_count'
	with open(filename, 'r') as fh:
		for line in fh:
			line = line.split('|')
			if len(line)!=3:
				continue
			country = line[0]
			count = line[1]
			active_count = line[2]
			value = {}
			value['country'] = country
			value['count'] = count
			value['count_active'] = active_count
			country_list.append(value)
	return country_list

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
	#order series alphabetically:
	ret = sorted(ret, key= lambda x: x['name'].lstrip())
	return ret
	
#returns multiple bar series representing average bitrate measurements for devices in a given country,
#in a given timeframe:
def parse_bitrate_country_average(start_date,end_date,country,direction):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = database_helper.get_all_isps()
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
	#order series alphabetically:
	ret = sorted(ret, key= lambda x: x['name'].lstrip())
	return ret
	
#returns multiple bar series representing average bitrate measurements for devices under a given isp,
#in a given timeframe:
def parse_bitrate_isp_average(start_date,end_date,isp,direction,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	cities = database_helper.get_all_cities()
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
	#order series alphabetically:
	ret = sorted(ret, key= lambda x: x['name'].lstrip())
	return ret
	
#returns multiple bar series representing average LMRTT measurements for devices in a given city,
#in a given timeframe:
def parse_lmrtt_city_average(start_date,end_date,city):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = database_helper.get_all_isps()
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
	#sort series alphabetically:
	ret = sorted(ret, key= lambda x: x['name'].lstrip())
	return ret
	
#returns multiple bar series representing average LMRTT measurements for devices in a given country,
#in a given timeframe:
def parse_lmrtt_country_average(start_date,end_date,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = database_helper.get_all_isps()
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
	#sort series alphabetically:
	ret = sorted(ret, key= lambda x: x['name'].lstrip())
	return ret

#returns multiple bar series representing average LMRTT measurements for devices under a given ISP,
#in a given timeframe:
def parse_lmrtt_isp_average(start_date,end_date,isp,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	cities = database_helper.get_all_cities()
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
	#sort series alphabetically:
	ret = sorted(ret, key= lambda x: x['name'].lstrip())
	return ret
	
#returns multiple bar series representing average RTT measurements for devices in a given city,
#in a given timeframe:
def parse_rtt_city_average(start_date,end_date,city):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = database_helper.get_all_isps()
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
	#sort series alphabetically:
	ret = sorted(ret, key= lambda x: x['name'].lstrip())
	return ret
	
#returns multiple bar series representing average RTT measurements for devices in a given country,
#in a given timeframe:
def parse_rtt_country_average(start_date,end_date,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	isps = database_helper.get_all_isps()
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
	#sort series alphabetically:
	ret = sorted(ret, key= lambda x: x['name'].lstrip())
	return ret
	
#returns multiple bar series representing average RTT measurements for devices under a given ISP,
#in a given timeframe:
def parse_rtt_isp_average(start_date,end_date,isp,country):
	data = []
	ret = []
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	cities = database_helper.get_all_cities()
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
	#sort series alphabetically:
	ret = sorted(ret, key= lambda x: x['name'].lstrip())
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
def parse_bitrate_measurements(hash, dir):
	result = []
	data = []
	device = database_helper.get_device_by_hash(hash).replace(':','')
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
def parse_underload_measurements(hash):
	result = []
	data = []
	device = database_helper.get_device_by_hash(hash).replace(':','')
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
def parse_rtt_measurements(hash):
	result = []
	data = []
	dstips = []
	device = database_helper.get_device_by_hash(hash).replace(':','')
	filename = settings.PROJECT_ROOT + '/summary/measurements/rtt/' + device
	#garbage characters to be removed:
	remove = ')("\n'
	ipr = database_helper.get_server_list()
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
def parse_lmrtt_measurements(hash):
	data = []
	result = []
	device = database_helper.get_device_by_hash(hash).replace(':','')
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
def parse_shaperate_measurements(hash):
	data = []
	result = []
	device = database_helper.get_device_by_hash(hash).replace(':','')
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
def parse_capacity_measurements(hash):
	data = []
	result = []
	device = database_helper.get_device_by_hash(hash).replace(':','')
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

		