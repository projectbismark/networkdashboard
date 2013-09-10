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
#import fcntl

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
	# all_devices = Devicedetails.objects.all().values('deviceid')
	# count = 0
	# t0 = datetime.now()
	# for device in all_devices:
		# device = device['deviceid']
		# database_helper.update_bitrate(device)
		# database_helper.update_rtt(device)
		# database_helper.update_lmrtt(device)
		# database_helper.update_shaperate(device)
		# database_helper.update_capacity(device)
		# database_helper.update_unload(device)
		# lock.release()
		# count+=1
		# t1 = datetime.now()
		# print t1-t0
		# print str(len(all_devices)-count) + " remaining"
	#rite_rtt_measurements()
	#write_lmrtt_measurements()
	#write_bitrate_measurements()
	write_shaperate_measurements()
	write_underload_measurements()
	return

def write_rtt_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	count = 0
	t0 = datetime.now()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/rtt/' + device2
		f = open(filename, 'w')
		params = []
		params.append(d.deviceid)
		SQL = "SELECT \
			m_rtt.eventstamp, average, dstip \
			FROM m_rtt JOIN devicedetails on devicedetails.deviceid=m_rtt.deviceid \
			WHERE m_rtt.deviceid=%s AND m_rtt.average<3000 AND m_rtt.average>0"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		for r in records:
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			dstip = r['dstip']
			line = str(eventstamp) + ',' + str(avg) + ',' + dstip + '\n'
			f.write(line)
		f.close()
		count += 1
		t1 = datetime.now()
		print t1-t0
		print str(len(devices)-count) + " remaining"
	cursor.close()
	return

def write_lmrtt_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	count = 0
	t0 = datetime.now()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt/' + device2
		f = open(filename, 'w')
		params = []
		params.append(d.deviceid)
		SQL = "SELECT \
			m_lmrtt.eventstamp, average \
			FROM m_lmrtt JOIN devicedetails on devicedetails.deviceid=m_lmrtt.deviceid \
			WHERE m_lmrtt.deviceid=%s AND m_lmrtt.average<3000 AND m_lmrtt.average>0"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		for r in records:
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			line = str(eventstamp) + ',' + str(avg) + '\n'
			f.write(line)
		f.close()
		count += 1
		t1 = datetime.now()
		print t1-t0
		print str(len(devices)-count) + " remaining"
	cursor.close()
	return

def write_bitrate_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	count = 0
	t0 = datetime.now()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate/' + device2
		f = open(filename, 'w')
		params = []
		params.append(d.deviceid)
		SQL = "SELECT \
			m_bitrate.eventstamp, average, direction, toolid \
			FROM m_bitrate JOIN devicedetails on devicedetails.deviceid=m_bitrate.deviceid \
			WHERE m_bitrate.deviceid=%s AND m_bitrate.average>0"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		for r in records:
			direction = r['direction']
			if direction=='' or direction==None:
				continue
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			toolid = r['toolid']
			line = str(eventstamp) + ',' + str(avg) + ',' + str(direction) + ',' + str(toolid) + '\n'
			f.write(line)
		f.close()
		count += 1
		t1 = datetime.now()
		print t1-t0
		print str(len(devices)-count) + " remaining"
	cursor.close()
	return
	
def write_shaperate_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	count = 0
	t0 = datetime.now()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/shaperate/' + device2
		f = open(filename, 'w')
		params = []
		params.append(d.deviceid)
		SQL = "SELECT \
			m_shaperate.eventstamp, average, direction \
			FROM m_shaperate JOIN devicedetails on devicedetails.deviceid=m_shaperate.deviceid \
			WHERE m_shaperate.deviceid=%s"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		for r in records:
			direction = r['direction']
			if direction=='' or direction==None:
				continue
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			line = str(eventstamp) + ',' + str(avg) + ',' + str(direction) + '\n'
			f.write(line)
		f.close()
		count += 1
		t1 = datetime.now()
		print t1-t0
		print str(len(devices)-count) + " remaining"
	cursor.close()
	return
	
def write_underload_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	count = 0
	t0 = datetime.now()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/underload/' + device2
		f = open(filename, 'w')
		params = []
		params.append(d.deviceid)
		SQL = "SELECT \
			m_ulrttdw.eventstamp, average, direction \
			FROM m_ulrttdw JOIN devicedetails on devicedetails.deviceid=m_ulrttdw.deviceid \
			WHERE m_ulrttdw.deviceid=%s"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		for r in records:
			direction = r['direction']
			if direction=='' or direction==None:
				continue
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			line = str(eventstamp) + ',' + str(avg) + ',' + str(direction) + '\n'
			f.write(line)
		SQL = "SELECT \
			m_ulrttup.eventstamp, average, direction \
			FROM m_ulrttup JOIN devicedetails on devicedetails.deviceid=m_ulrttup.deviceid \
			WHERE m_ulrttup.deviceid=%s"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		for r in records:
			direction = r['direction']
			if direction=='' or direction==None:
				continue
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			line = str(eventstamp) + ',' + str(avg) + ',' + str(direction) + '\n'
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
	