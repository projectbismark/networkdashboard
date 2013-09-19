from django.core.management.base import NoArgsCommand
from networkdashboard.summary import database_helper, geoip_helper
from networkdashboard.summary.models import *
from django.conf import settings
import os
import psycopg2
import sys

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		update_devicedetails()
	
def update_devicedetails():
	devices = Devicedetails.objects.all()
	servers = IpResolver.objects.all()
	conn_string = "host='localhost' dbname='" + settings.MGMT_DB + "' user='"+ settings.MGMT_USERNAME  +"' password='" + \
		settings.MGMT_PASS + "'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	for d in devices:
		id = "OW" + d.deviceid.upper().replace(":","")
		cursor.execute("select ip from devices where id='" + id + "'")
		iprow = (cursor.fetchone())
		if iprow == None:
			continue
		d.ip = iprow[0]
		country_code = geoip_helper.get_country_code_by_ip(iprow)
		country_name = geoip_helper.get_country_name_by_ip(iprow)
		isp = geoip_helper.get_provider_by_ip(iprow)
		city_name = geoip_helper.get_city_by_ip(iprow)
		# pygeoip names are encoded using cp1252, postgres expects utf8: 
		if city_name != "" and city_name != None:
			city_name = city_name.decode('cp1252').encode('utf8')
			d.geoip_city = city_name
		if country_code != "" and country_code != None:
			country_code = country_code.decode('cp1252').encode('utf8')
			d.country_code = country_code
		if country_name != "" and country_name != None:
			country_name = country_name.decode('cp1252').encode('utf8')
			d.geoip_country = country_name
		if isp != "" and isp != None:
			isp = isp.decode('cp1252').encode('utf8')
			d.geoip_isp = isp
		d.save()
	return
	
def update_server_locs()
	servers = IpResolver.objects.all()
	for s in servers:
		lat = geoip_helper.get_latitude_by_ip(s.ip)
		lon = geoip_helper.get_longitude_by_ip(s.ip)
		s.latitude=lat
		s.longitude=lon
		s.save()
	return
