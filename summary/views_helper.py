from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
from operator import itemgetter
from django.db import transaction
from django.conf import settings
import psycopg2
import hashlib
import database_helper
import data_helper


#returns line series data representing RTT measurements for devices under a particular isp:	
def compare_line_rtt_by_isp(max_results,isp,country,earliest,latest):	
	result = []
	#all devices under given isp:
	devices = database_helper.get_details_by_isp(isp)
	if country!='none':
		devices = devices.filter(geoip_country=country)
	for d in devices:
		if d.geoip_city!='' and d.geoip_city!=None:
			data = []
			if len(result)<max_results:
				try:
					data = data_helper.parse_rtt_compare(d.deviceid,earliest,latest,d.geoip_city)
				except:
					continue
				#no measurements:
				if len(data['data'])==0:
					continue
				result.append(data)
	#sort series alphabetically:
	result = sorted(result, key = lambda x: x['name'].lstrip())
	return result

#returns line series data representing LMRTT measurements for devices under a particular isp:	
def compare_line_lmrtt_by_isp(max_results,isp,country,earliest,latest):	
	result = []
	#all devices under given isp:
	devices = database_helper.get_details_by_isp(isp)
	if country!='none':
		devices = devices.filter(geoip_country=country)
	for d in devices:
		if d.geoip_city!='' and d.geoip_city!=None:
			data = []
			if len(result)<max_results:
				try:
					data = data_helper.parse_lmrtt_compare(d.deviceid,earliest,latest,d.geoip_city)
				except:
					continue
				#no measurements:
				if len(data['data'])==0:
					continue
				result.append(data)
	#sort series alpahetically:
	result = sorted(result, key = lambda x: x['name'].lstrip())
	return result

#returns line series data representing RTT measurements for devices in a particular city:	
def compare_line_rtt_by_city(max_results,city,earliest,latest):	
	result = []
	#all devices for given city:
	devices = database_helper.get_details_by_city(city)
	for d in devices:
		if d.geoip_isp!='' and d.geoip_isp!=None:
			data = []
			if len(result)<max_results:
				try:
					data = data_helper.parse_rtt_compare(d.deviceid,earliest,latest,d.geoip_isp)
				except:
					continue
				#no measurements:
				if len(data['data'])==0:
					continue
				result.append(data)
	#sort series alphabetically:
	result = sorted(result, key = lambda x: x['name'].lstrip())
	return result

#returns line series data representing lmrtt measurements averaged by ISP for a particular city
def compare_line_lmrtt_by_city(max_results, city, earliest, latest):
	result = []
	#all devices for given city
	devices = database_helper.get_details_by_city(city)
	for d in devices:
		if d.geoip_isp!='' and d.geoip_isp!=None:
			data = []
			if len(result)<max_results:
				try:
					data = data_helper.parse_lmrtt_compare(d.deviceid,earliest,latest,d.geoip_isp)
				except:
					continue
				#no measurements:
				if len(data['data'])==0:
					continue
				result.append(data)
	#order series alphabetically:
	result = sorted(result, key = lambda x: x['name'].lstrip())
	return result

def compare_line_bitrate_by_isp(max_results,isp,country,direction,earliest,latest):
	result = []
	#all devices under given isp:
	devices = database_helper.get_details_by_isp(isp)
	#if country is specified, only devices for the given ISP and country are shown:
	if country!='none':
		devices = devices.filter(geoip_country=country)
	for d in devices:
		if d.geoip_city!='' and d.geoip_city!=None:
			data = []
			if len(result)<max_results:
				try:
					data = data_helper.parse_bitrate_compare(d.deviceid,earliest,latest,direction,d.geoip_city)
				except:
					continue
				#no measurements:
				if len(data['data'])==0:
					continue
				result.append(data)
	#order series alphabetically:
	result = sorted(result, key = lambda x: x['name'].lstrip())
	return result

#returns column series data representing bitrate measurements averaged by ISP for a particular city:
def compare_line_bitrate_by_city(max_results,city,direction,earliest,latest):
	result = []
	#all devices for given city
	devices = database_helper.get_details_by_city(city)
	for d in devices:
		if d.geoip_isp!='' and d.geoip_isp!=None:
			data = []
			if len(result)<max_results:
				try:
					data = data_helper.parse_bitrate_compare(d.deviceid,earliest,latest,direction,d.geoip_isp)
				except:
					continue
				#no measurements:
				if len(data['data'])==0:
					continue
				result.append(data)
	#order series alphabetically:
	result = sorted(result, key = lambda x: x['name'].lstrip())
	return result

#gets the location of the device. This is the location as specified by the user, as opposed to
#resolved from IP:
def get_location(hash):
	device = database_helper.get_device_by_hash(hash)
	details = database_helper.get_details_by_deviceid(device)
	if details.count()>0:
		return (details[0].city + ", " + details[0].country)  
	return "unavailable"
	
#returns an html page for a particular device for a user who owns that device 
#and forwards data to that page:
def get_response_for_devicehtml(device_details):
	first = data_helper.get_first_measurement(device_details.deviceid)
	last = data_helper.get_last_measurement(device_details.deviceid)
	deviceid = device_details.deviceid.replace(':', '').lower()
	is_default = device_details.is_default
	hashkey = device_details.hashkey
	isp = device_details.isp
	servicetype = device_details.servicetype
	serviceplan = device_details.serviceplan
	downloadrate = device_details.downloadrate
	uploadrate = device_details.uploadrate
	name = device_details.name
	tab = '1'
	start = '0'
	end = '0'
	return render_to_response('device.html', {'is_default':is_default, 'hashkey':hashkey, \
	'isp':isp, 'servicetype':servicetype, 'serviceplan':serviceplan, 'downloadrate': downloadrate, \
	'uploadrate': uploadrate, 'name': name, 'first_update': first, 'last_update': last, 'deviceid':deviceid, 'tab':tab, 'start': start, 'end':end})

#returns an html page for a particular device for a user who does not own that deviec
#and forwards data to that page:
def get_response_for_shared_device(device_details,tab,start,end):
	first = data_helper.get_first_measurement(device_details.deviceid)
	last = data_helper.get_last_measurement(device_details.deviceid)
	deviceid = device_details.deviceid.replace(':', '').lower()
	is_default = device_details.is_default
	hashkey = device_details.hashkey
	isp = device_details.isp
	servicetype = device_details.servicetype
	serviceplan = device_details.serviceplan
	downloadrate = device_details.downloadrate
	uploadrate = device_details.uploadrate
	name = device_details.name
	return render_to_response('shared_device.html', {'is_default':is_default, 'hashkey':hashkey, \
	'isp':isp, 'servicetype':servicetype, 'serviceplan':serviceplan, 'downloadrate': downloadrate, \
	'uploadrate': uploadrate, 'name': name, 'first_update': first, 'last_update': last, 'tab': tab, 'start':start, 'end':end})
		
#gets device counts by country and sorts them alphabetically:
def get_sorted_country_data():
	#get list of dictionaries:
	country_data = data_helper.get_country_data()
	result = sorted(country_data, key=itemgetter('country'))
	return result

#gets device counts by city and sorts them alphabetically:	
def get_sorted_city_data():
	#get list of dictionaries:
	city_data = data_helper.get_city_data()
	result = sorted(city_data, key=itemgetter('city'))
	return result

#gets device counts by isp and sorts them alphabetically:	
def get_sorted_isp_data():
	#get list of dictionaries:
	isp_data = data_helper.get_isp_data()
	result = sorted(isp_data, key=itemgetter('isp'))
	return result

