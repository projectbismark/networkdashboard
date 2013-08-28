from django.core.management.base import NoArgsCommand
from networkdashboard.summary import database_helper, datetime_helper
from networkdashboard.summary.models import *
from django.conf import settings
from datetime import datetime
import os
import json
import psycopg2
import psycopg2.extras
import time
from django.core import serializers
import sys
import fcntl

class UpdateLock:
	def __init__(self, filename):
		self.filename = filename
		self.handle = open(filename, 'w')
		
	def acquire(self):
		try:
			# non blocking
			fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
			return True
		except IOError:
			return False
		
	def release(self):
		fcntl.flock(self.handle, fcntl.LOCK_UN)
		
	def __del__(self):
		self.handle.close()

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		update_json()
	
def update_json():
	# lock = UpdateLock('/tmp/UpdateLock.tmp')
	# if (lock.acquire()):
	all_devices = Devicedetails.objects.all().values('deviceid')
	count = 0
	t0 = datetime.now()
	for device in all_devices:
		device = device['deviceid']
		database_helper.update_bitrate(device)
		# database_helper.update_rtt(device)
		database_helper.update_lmrtt(device)
		database_helper.update_shaperate(device)
		database_helper.update_capacity(device)
		database_helper.update_unload(device)
		#lock.release()
		count+=1
		t1 = datetime.now()
		print t1-t0
		print str(len(all_devices)-count) + " remaining"
	write_rtt_measurements()
	return

def write_rtt_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	count = 0
	t0 = datetime.now()
	ipr = IpResolver.objects.all()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/' + device2
		f = open(filename, 'w')
		params = []
		params.append(d.deviceid)
		SQL = "SELECT \
			m_rtt.eventstamp, average, dstip, country, city, isp \
			FROM m_rtt JOIN devicedetails on devicedetails.deviceid=m_rtt.deviceid \
			WHERE m_rtt.deviceid=%s;"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		for r in records:
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			mserver = ''
			country = r['country']
			city = r['city']
			isp = r['isp']
			try:
				mserver = ipr.filter(ip=r['dstip'])[0].location
			except:
				continue
			line = str(eventstamp) + ',' + str(avg) + ',' + mserver + ',' + country + ',' + city + ',' + isp +  '\n'
			f.write(line)
		f.close()
		count += 1
		t1 = datetime.now()
		print t1-t0
		print str(len(devices)-count) + " remaining"
	cursor.close()
	return		
	
	
def get_dict_cursor():
    conn_string = "host='" + settings.DATABASES['default']['HOST'] + \
                   "' dbname='" + settings.DATABASES['default']['NAME'] + \
                   "' user='" + settings.DATABASES['default']['USER'] + \
                   "' password='" + settings.DATABASES['default']['PASSWORD'] + "'";
                   
    conn = psycopg2.connect(conn_string)
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	