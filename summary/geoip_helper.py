from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from django.conf import settings
from networkdashboard.summary.models import *
import isp_mappings
import database_helper
import pygeoip
import psycopg2
from django.core.cache import cache

#returns a geoip record for a given IP:
def get_location_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	gi_rec = gi.record_by_addr(ip)
	return gi_rec

#returns latitudinal coordinate for the given IP:
def get_latitude_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	loc = gi.record_by_addr(ip)
	return loc['latitude']

#returns longitudinal coordinate for the given IP:
def get_longitude_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	loc = gi.record_by_addr(ip)
	return loc['longitude']

#resolves IP to city:	
def get_city_by_ip(ip):
	rec = get_record_by_ip(ip)
	if rec != None:
		return rec['city']
	else:
		return ''
		
#uses geoip in an indirect fashion to lookup country by city:
def get_country_by_city(city):
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	ips = database_helper.get_ip_list()
	for ip in ips:
		try:
			record = gi.record_by_addr(ip[0])
			if record['city']==city:
				return record['country_name']
		except:
			continue
	return ''

#resolves IP to country code:
def get_country_code_by_ip(ip):
	rec = get_record_by_ip(ip)
	if rec != None:
		return rec['country_code']
	else:
		return ''

#resolves IP to country name:		
def get_country_name_by_ip(ip):
	rec = get_record_by_ip(ip)
	if rec != None:
		return rec['country_name']
	else:
		return ''
	
#resolves IP to ISP:
def get_provider_by_ip(ip):
	gi = pygeoip.GeoIP(settings.GEOIP_ASN_LOCATION,pygeoip.MEMORY_CACHE)
	mappings = isp_mappings.mappings
	try:
		isp = gi.org_by_addr(ip[0]).lstrip("AS0123456789")
	except:
		return "unknown"
	for m in mappings:
		if(isp.lower().find(m[0].lower())!=-1):
			isp = m[1]		
	return isp

#returns a geoip record for the given IP:
def get_record_by_ip(ip):
	if len(ip)>0:
		gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
		return gi.record_by_addr(ip[0])
	else:
		return ""

