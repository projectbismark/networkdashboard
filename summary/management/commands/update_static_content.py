from django.core.management.base import NoArgsCommand
from networkdashboard.summary import database_helper, datetime_helper, geoip_helper
from networkdashboard.summary.models import *
from django.conf import settings
from datetime import datetime
import os
import json
import psycopg2
import psycopg2.extras
import time
from django.core import serializers
import pygeoip
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
	lock = UpdateLock('/tmp/UpdateLock.tmp')
	if (lock.acquire()):
		write_devices()
		write_city_count()
		write_country_count()
		write_isp_count()
		write_bitrate_measurements()
		write_shaperate_measurements()
		write_underload_measurements()
		write_capacity_measurements()
		dump_all_latencies()
		write_coord_data()
		write_lmrtt_measurements()
		write_rtt_measurements()
		write_rtt_city_averages()
		write_lmrtt_city_averages()
		write_bitrate_city_averages()
		write_rtt_country_averages()
		write_lmrtt_country_averages()
		write_bitrate_country_averages()
		write_rtt_isp_averages()
		write_lmrtt_isp_averages()
		write_bitrate_isp_averages()
	return
	
def write_devices():
	devices = Devicedetails.objects.all()
	filename = settings.PROJECT_ROOT + '/summary/device_data/devices'
	cursor = get_dict_cursor()
	file = open(filename, 'w')
	for d in devices:
		SQL = ''
		last = ''
		params = []
		latest = 0
		params.append(d.deviceid)
		device2 = d.deviceid.replace(':','')
		filename2 = settings.PROJECT_ROOT + '/summary/measurements/rtt/' + device2
		try:
			with open(filename2, 'r') as fh:
				for line in fh:
					last = line
		except:
			pass
		if len(last)>0:
			last=last.split('|')
			latest = last[0]
		SQL = "SELECT \
				deviceid, eventstamp, geoip_city, geoip_country, geoip_isp \
				FROM devicedetails \
				WHERE deviceid=%s"
		cursor.execute(SQL,params)
		rec = cursor.fetchone()
		id = rec['deviceid']
		if id==None:
			id='none'
		eventstamp = datetime_helper.datetime_to_JSON(rec['eventstamp'])
		city = rec['geoip_city']
		if city==None:
			city='none'
		country = rec['geoip_country']
		if country==None:
			country='none'
		isp = rec['geoip_isp']
		if isp==None:
			isp='none'
		line = id + '|' + str(eventstamp) + '|' + city.encode('utf-8') + '|' + country.encode('utf-8') + '|' + isp.encode('utf-8') + '|' + str(latest) + '\n'
		file.write(line)
	file.close()
	cursor.close()
	return

def write_rtt_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/rtt/' + device2
		SQL = ''
		last = ''
		params = []
		params.append(d.deviceid)
		try:
			with open(filename, 'r') as fh:
				# probably a better way to do this:
				for line in fh:
					last = line
		except:
			pass
		f = open(filename, 'a')
		if last!='':
			last=last.split('|')
			latest = datetime.fromtimestamp(int(last[0])/1000)
			params.append(latest)
			SQL = "SELECT \
				m_rtt.eventstamp, average, dstip \
				FROM m_rtt JOIN devicedetails on devicedetails.deviceid=m_rtt.deviceid \
				WHERE m_rtt.deviceid=%s AND m_rtt.average<3000 AND m_rtt.average>0 AND m_rtt.eventstamp>%s"
		else:
			SQL = "SELECT \
			m_rtt.eventstamp, average, dstip \
			FROM m_rtt JOIN devicedetails on devicedetails.deviceid=m_rtt.deviceid \
			WHERE m_rtt.deviceid=%s AND m_rtt.average<3000 AND m_rtt.average>0"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		records = sorted(records,key=lambda x: datetime_helper.datetime_to_JSON(x['eventstamp']))
		for r in records:
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			dstip = r['dstip']
			line = str(eventstamp) + '|' + str(avg) + '|' + dstip + '\n'
			f.write(line)
		f.close()
	cursor.close()
	return
	
def write_rtt_country_averages():
	dstip='8.8.8.8'
	cursor = get_dict_cursor()
	filename = settings.PROJECT_ROOT + '/summary/measurements/rtt_averages/country'
	f = open(filename, 'w')
	params = []
	params.append(dstip)
	SQL =  "SELECT \
			geoip_isp AS isp, \
			geoip_country AS country, \
			m_rtt.eventstamp::date AS day, \
			count(distinct m_rtt.srcip) AS ndevices, \
			count(*) AS nmeasurements, \
			avg(m_rtt.average) AS latency \
			FROM m_rtt \
			JOIN devicedetails AS d ON d.deviceid = m_rtt.deviceid \
			WHERE m_rtt.dstip = %s AND m_rtt.average>0 AND m_rtt.average<3000 AND geoip_country!='' AND geoip_isp != ''  \
			GROUP BY day, d.geoip_country, d.geoip_isp;"
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	for r in records:
		avg = r['latency']
		m_count = r['nmeasurements']
		day = datetime_helper.datetime_to_JSON(r['day'])
		country = r['country']
		isp = r['isp']
		d_count = r['ndevices']
		line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + country + '|' + str(d_count) + '|' + isp + '\n'
		f.write(line)
	f.close()
	cursor.close()
	return
	
def write_lmrtt_country_averages():
	cursor = get_dict_cursor()
	filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt_averages/country'
	f = open(filename, 'w')
	SQL =  "SELECT \
			geoip_isp AS isp, \
			geoip_country AS country, \
			m_lmrtt.eventstamp::date AS day, \
			count(distinct m_lmrtt.srcip) AS ndevices, \
			count(*) AS nmeasurements, \
			avg(m_lmrtt.average) AS latency \
			FROM m_lmrtt \
			JOIN devicedetails AS d ON d.deviceid = m_lmrtt.deviceid \
			WHERE m_lmrtt.average>0 AND m_lmrtt.average<3000 AND geoip_country!='' AND geoip_isp!=''  \
			GROUP BY day, d.geoip_country, d.geoip_isp;"
	cursor.execute(SQL)
	records = cursor.fetchall()
	for r in records:
		avg = r['latency']
		m_count = r['nmeasurements']
		day = datetime_helper.datetime_to_JSON(r['day'])
		country = r['country']
		isp = r['isp']
		d_count = r['ndevices']
		line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + country + '|' + str(d_count) + '|' + isp + '\n'
		f.write(line)
	f.close()
	cursor.close()
	return

def write_bitrate_country_averages():
	cursor = get_dict_cursor()
	filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate_averages/country'
	f = open(filename, 'w')
	SQL =  "SELECT \
			geoip_isp AS isp, \
			direction AS dir, \
			geoip_country AS country, \
			m_bitrate.eventstamp::date AS day, \
			count(distinct m_bitrate.srcip) AS ndevices, \
			count(*) AS nmeasurements, \
			avg(m_bitrate.average) AS bitrate \
			FROM m_bitrate \
			JOIN devicedetails AS d ON d.deviceid = m_bitrate.deviceid \
			WHERE  m_bitrate.average>0 AND geoip_country!='' AND toolid='NETPERF_3' AND geoip_isp != ''  \
			GROUP BY day, d.geoip_country, dir, d.geoip_isp;"
	cursor.execute(SQL)
	records = cursor.fetchall()
	for r in records:
		try:
			avg = r['bitrate']
			m_count = r['nmeasurements']
			day = datetime_helper.datetime_to_JSON(r['day'])
			country = r['country']
			isp = r['isp']
			d_count = r['ndevices']
			dir = r['dir']
			line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + country + '|' + str(d_count) + '|' + dir + '|' + isp + '\n'
			f.write(line)
		except:
			continue
	f.close()
	cursor.close()
	return

def write_rtt_city_averages():
	dstip='8.8.8.8'
	cursor = get_dict_cursor()
	filename = settings.PROJECT_ROOT + '/summary/measurements/rtt_averages/city'
	f = open(filename, 'w')
	params = []
	params.append(dstip)
	SQL =  "SELECT \
			geoip_isp AS isp, \
			geoip_city AS city, \
			m_rtt.eventstamp::date AS day, \
			count(distinct m_rtt.srcip) AS ndevices, \
			count(*) AS nmeasurements, \
			avg(m_rtt.average) AS latency \
			FROM m_rtt \
			JOIN devicedetails AS d ON d.deviceid = m_rtt.deviceid \
			WHERE m_rtt.dstip = %s AND m_rtt.average>0 AND m_rtt.average<3000 AND geoip_city!='' AND geoip_isp!=''  \
			GROUP BY day, d.geoip_city, d.geoip_isp;"
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	for r in records:
		avg = r['latency']
		m_count = r['nmeasurements']
		day = datetime_helper.datetime_to_JSON(r['day'])
		city = r['city']
		isp = r['isp']
		d_count = r['ndevices']
		line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + city.encode('utf-8') + '|' + str(d_count) + '|' + isp.encode('utf-8') + '\n'
		f.write(line)
	f.close()
	cursor.close()
	return

def write_lmrtt_city_averages():
	cursor = get_dict_cursor()
	filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt_averages/city'
	f = open(filename, 'w')
	SQL =  "SELECT \
			geoip_isp AS isp, \
			geoip_city AS city, \
			m_lmrtt.eventstamp::date AS day, \
			count(distinct m_lmrtt.srcip) AS ndevices, \
			count(*) AS nmeasurements, \
			avg(m_lmrtt.average) AS latency \
			FROM m_lmrtt \
			JOIN devicedetails AS d ON d.deviceid = m_lmrtt.deviceid \
			WHERE m_lmrtt.average>0 AND m_lmrtt.average<3000 AND geoip_city!='' AND geoip_isp!=''  \
			GROUP BY day, d.geoip_city, d.geoip_isp;"
	cursor.execute(SQL)
	records = cursor.fetchall()
	for r in records:
		avg = r['latency']
		m_count = r['nmeasurements']
		day = datetime_helper.datetime_to_JSON(r['day'])
		city = r['city']
		isp = r['isp']
		d_count = r['ndevices']
		line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + city.encode('utf-8') + '|' + str(d_count) + '|' + isp.encode('utf-8') + '\n'
		f.write(line)
	f.close()
	cursor.close()
	return

def write_bitrate_city_averages():
	cursor = get_dict_cursor()
	filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate_averages/city'
	f = open(filename, 'w')
	SQL =  "SELECT \
			geoip_isp AS isp, \
			direction AS dir,\
			geoip_city AS city, \
			m_bitrate.eventstamp::date AS day, \
			count(distinct m_bitrate.srcip) AS ndevices, \
			count(*) AS nmeasurements, \
			avg(m_bitrate.average) AS bitrate \
			FROM m_bitrate \
			JOIN devicedetails AS d ON d.deviceid = m_bitrate.deviceid \
			WHERE m_bitrate.average>0 AND geoip_city!='' AND toolid='NETPERF_3' AND geoip_isp!=''  \
			GROUP BY day, d.geoip_city, d.geoip_isp, dir;"
	cursor.execute(SQL)
	records = cursor.fetchall()
	for r in records:
		try:
			avg = r['bitrate']
			m_count = r['nmeasurements']
			day = datetime_helper.datetime_to_JSON(r['day'])
			city = r['city']
			isp = r['isp']
			d_count = r['ndevices']
			dir = r['dir']
			line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + city.encode('utf-8') + '|' + str(d_count) + '|' + dir + '|' + isp.encode('utf-8') + '\n'
			f.write(line)
		except:
			continue
	f.close()
	cursor.close()
	return
	
def write_rtt_isp_averages():
	dstip='8.8.8.8'
	cursor = get_dict_cursor()
	filename = settings.PROJECT_ROOT + '/summary/measurements/rtt_averages/isp'
	f = open(filename, 'w')
	params = []
	params.append(dstip)
	SQL =  "SELECT \
			geoip_isp AS isp , \
			geoip_city AS city, \
			geoip_country AS country, \
			m_rtt.eventstamp::date AS day, \
			count(distinct m_rtt.srcip) AS ndevices, \
			count(*) AS nmeasurements, \
			avg(m_rtt.average) AS latency \
			FROM m_rtt \
			JOIN devicedetails AS d ON d.deviceid = m_rtt.deviceid \
			WHERE m_rtt.dstip = %s AND m_rtt.average>0 AND m_rtt.average<3000 AND geoip_isp!='' AND geoip_country!='' AND geoip_city!=''  \
			GROUP BY day, d.geoip_isp, d.geoip_country, d.geoip_city;"
	cursor.execute(SQL,params)
	records = cursor.fetchall()
	for r in records:
		avg = r['latency']
		m_count = r['nmeasurements']
		day = datetime_helper.datetime_to_JSON(r['day'])
		isp = r['isp']
		country = r['country']
		city = r['city']
		d_count = r['ndevices']
		line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + isp.encode('utf-8') + '|' + str(d_count) + '|' + country.encode('utf-8') + '|' + city.encode('utf-8') + '\n'
		f.write(line)
	f.close()
	cursor.close()
	return

def write_lmrtt_isp_averages():
	cursor = get_dict_cursor()
	filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt_averages/isp'
	f = open(filename, 'w')
	SQL =  "SELECT \
			geoip_country AS country, \
			geoip_city AS city, \
			geoip_isp AS isp, \
			m_lmrtt.eventstamp::date AS day, \
			count(distinct m_lmrtt.srcip) AS ndevices, \
			count(*) AS nmeasurements, \
			avg(m_lmrtt.average) AS latency \
			FROM m_lmrtt \
			JOIN devicedetails AS d ON d.deviceid = m_lmrtt.deviceid \
			WHERE m_lmrtt.average>0 AND m_lmrtt.average<3000 AND geoip_isp!='' AND geoip_country!='' AND geoip_city!=''  \
			GROUP BY day, d.geoip_isp, d.geoip_country, d.geoip_city;"
	cursor.execute(SQL)
	records = cursor.fetchall()
	for r in records:
		avg = r['latency']
		m_count = r['nmeasurements']
		day = datetime_helper.datetime_to_JSON(r['day'])
		isp = r['isp']
		country = r['country']
		city = r['city']
		d_count = r['ndevices']
		line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + isp.encode('utf-8') + '|' + str(d_count) + '|' + country.encode('utf-8') + '|' + city.encode('utf-8') + '\n'
		f.write(line)
	f.close()
	cursor.close()
	return

def write_bitrate_isp_averages():
	cursor = get_dict_cursor()
	filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate_averages/isp'
	f = open(filename, 'w')
	SQL =  "SELECT \
			geoip_country as country, \
			geoip_city as city, \
			direction AS dir, \
			geoip_isp AS isp , \
			m_bitrate.eventstamp::date AS day, \
			count(distinct m_bitrate.srcip) AS ndevices, \
			count(*) AS nmeasurements, \
			avg(m_bitrate.average) AS latency \
			FROM m_bitrate \
			JOIN devicedetails AS d ON d.deviceid = m_bitrate.deviceid \
			WHERE m_bitrate.average>0 AND geoip_isp!='' AND toolid='NETPERF_3' AND geoip_city!='' AND geoip_country!=''  \
			GROUP BY day, d.geoip_isp, dir, d.geoip_country, d.geoip_city;"
	cursor.execute(SQL)
	records = cursor.fetchall()
	for r in records:
		try:
			avg = r['latency']
			m_count = r['nmeasurements']
			day = datetime_helper.datetime_to_JSON(r['day'])
			isp = r['isp']
			city = r['city']
			country = r['country']
			d_count = r['ndevices']
			dir = r['dir']
			line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + isp.encode('utf-8') + '|' + str(d_count) + '|' + dir + '|' + country.encode('utf-8') + '|' + city.encode('utf-8') + '\n'
			f.write(line)
		except:
			continue
	f.close()
	cursor.close()
	return

def write_lmrtt_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/lmrtt/' + device2
		SQL = ""
		last = ""
		params = []
		params.append(d.deviceid)
		try:
			with open(filename, 'r') as fh:
				# probably a better way to do this:
				for line in fh:
					last = line
		except:
			pass
		f = open(filename, 'a')
		if last!='':
			last=last.split('|')
			latest = datetime.fromtimestamp(int(last[0])/1000)
			params.append(latest)
			SQL = "SELECT \
				m_lmrtt.eventstamp, average \
				FROM m_lmrtt JOIN devicedetails on devicedetails.deviceid=m_lmrtt.deviceid \
				WHERE m_lmrtt.deviceid=%s AND m_lmrtt.average<3000 AND m_lmrtt.average>0 AND m_lmrtt.eventstamp>%s"
		else:
			SQL = "SELECT \
				m_lmrtt.eventstamp, average \
				FROM m_lmrtt JOIN devicedetails on devicedetails.deviceid=m_lmrtt.deviceid \
				WHERE m_lmrtt.deviceid=%s AND m_lmrtt.average<3000 AND m_lmrtt.average>0"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		records = sorted(records,key=lambda x: datetime_helper.datetime_to_JSON(x['eventstamp']))
		for r in records:
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			line = str(eventstamp) + '|' + str(avg) + '\n'
			f.write(line)
		f.close()
	cursor.close()
	return

def write_bitrate_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/bitrate/' + device2
		SQL = ""
		last = ""
		params = []
		params.append(d.deviceid)
		try:
			with open(filename, 'r') as fh:
				# probably a better way to do this:
				for line in fh:
					last = line
		except:
			pass
		f = open(filename, 'a')
		if last!='':
			last=last.split('|')
			latest = datetime.fromtimestamp(int(last[0])/1000)
			params.append(latest)
			SQL = "SELECT \
				m_bitrate.eventstamp, average, direction, toolid \
				FROM m_bitrate JOIN devicedetails on devicedetails.deviceid=m_bitrate.deviceid \
				WHERE m_bitrate.deviceid=%s AND m_bitrate.average>0 AND m_bitrate.eventstamp>%s"
		else:
			SQL = "SELECT \
			m_bitrate.eventstamp, average, direction, toolid \
			FROM m_bitrate JOIN devicedetails on devicedetails.deviceid=m_bitrate.deviceid \
			WHERE m_bitrate.deviceid=%s AND m_bitrate.average>0"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		records = sorted(records,key=lambda x: datetime_helper.datetime_to_JSON(x['eventstamp']))
		for r in records:
			direction = r['direction']
			if direction=='' or direction==None:
				continue
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			toolid = r['toolid']
			line = str(eventstamp) + '|' + str(avg) + '|' + str(direction) + '|' + str(toolid) + '\n'
			f.write(line)
		f.close()
	cursor.close()
	return
	
def write_shaperate_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/shaperate/' + device2
		SQL = ""
		last = ""
		params = []
		params.append(d.deviceid)
		try:	
			with open(filename, 'r') as fh:
				# probably a better way to do this:
				for line in fh:
					last = line
		except:
			pass
		f = open(filename, 'a')
		if last!='':
			last=last.split('|')
			latest = datetime.fromtimestamp(int(last[0])/1000)
			params.append(latest)
			SQL = "SELECT \
				m_shaperate.eventstamp, average, direction \
				FROM m_shaperate JOIN devicedetails on devicedetails.deviceid=m_shaperate.deviceid \
				WHERE m_shaperate.deviceid=%s AND m_shaperate.eventstamp>%s"
		else:
			SQL = "SELECT \
			m_shaperate.eventstamp, average, direction \
			FROM m_shaperate JOIN devicedetails on devicedetails.deviceid=m_shaperate.deviceid \
			WHERE m_shaperate.deviceid=%s"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		records = sorted(records,key=lambda x: datetime_helper.datetime_to_JSON(x['eventstamp']))
		for r in records:
			direction = r['direction']
			if direction=='' or direction==None:
				continue
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			line = str(eventstamp) + '|' + str(avg) + '|' + str(direction) + '\n'
			f.write(line)
		f.close()
	cursor.close()
	return
	
def write_underload_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/underload/' + device2
		SQL = ""
		last = ""
		params = []
		params.append(d.deviceid)
		try:	
			with open(filename, 'r') as fh:
				# probably a better way to do this:
				for line in fh:
					last = line
		except:
			pass
		f = open(filename, 'a')
		if last!='':
			last=last.split('|')
			latest = datetime.fromtimestamp(int(last[0])/1000)
			params.append(latest)
			SQL1 = "SELECT \
				m_ulrttdw.eventstamp, average, direction \
				FROM m_ulrttdw JOIN devicedetails on devicedetails.deviceid=m_ulrttdw.deviceid \
				WHERE m_ulrttdw.deviceid=%s AND m_ulrttdw.eventstamp>%s"
			SQL2 = "SELECT \
				m_ulrttup.eventstamp, average, direction \
				FROM m_ulrttup JOIN devicedetails on devicedetails.deviceid=m_ulrttup.deviceid \
				WHERE m_ulrttup.deviceid=%s AND m_ulrttup.eventstamp>%s"
		else:
			SQL1 = "SELECT \
			m_ulrttdw.eventstamp, average, direction \
			FROM m_ulrttdw JOIN devicedetails on devicedetails.deviceid=m_ulrttdw.deviceid \
			WHERE m_ulrttdw.deviceid=%s"
			SQL2 = "SELECT \
			m_ulrttup.eventstamp, average, direction \
			FROM m_ulrttup JOIN devicedetails on devicedetails.deviceid=m_ulrttup.deviceid \
			WHERE m_ulrttup.deviceid=%s"
		cursor.execute(SQL1,params)
		records = cursor.fetchall()
		records = sorted(records,key=lambda x: datetime_helper.datetime_to_JSON(x['eventstamp']))
		for r in records:
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			line = str(eventstamp) + '|' + str(avg) + '|' + 'dw' + '\n'
			f.write(line)
		cursor.execute(SQL2,params)
		records = cursor.fetchall()
		for r in records:
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			line = str(eventstamp) + '|' + str(avg) + '|' + 'up' + '\n'
			f.write(line)
		f.close()
	cursor.close()
	return
	
def write_coord_data():
	gi = pygeoip.GeoIP(settings.GEOIP_SERVER_LOCATION,pygeoip.MEMORY_CACHE)
	filename = settings.PROJECT_ROOT + '/summary/measurements/map/coord_data'
	f = open(filename, 'w')
	devices = Devicedetails.objects.all()
	servers = IpResolver.objects.all()
	active_thresh = datetime_helper.get_daterange_start(7)
	for d in devices:
		try:
			id = d.deviceid
			if d.ip=="" or d.ip==None:
				continue
			loc = geoip_helper.getLocation(d.ip,gi)
			if loc==None:
				continue
			lat = str(geoip_helper.randomize_latitude(loc['latitude']))
			lon = str(loc['longitude'])
			hash = d.hashkey
			isp = d.geoip_isp
			active = 0
			server = 0
			if hash=="":
				continue
			recent_measurement_count = MBitrate.objects.filter(deviceid=id,eventstamp__gte=active_thresh).count()
			if recent_measurement_count>0:
				active=1
			line = hash + '|' + lat + '|' + lon + '|' + isp + '|' + str(active) + '|' + str(server) + '\n'
			f.write(line)
		except:
			continue
	for s in servers:
		try:
			isp = ""
			active = 1
			server = 1
			loc = geoip_helper.getLocation(s.ip,gi)
			if loc==None:
				continue
			lat = str(row_ip.latitude)
			lon = str(row_ip.longitude)
			hash = ""
			line = hash + '|' + lat + '|' + lon + '|' + isp + '|' + str(active) + '|' + str(server) + '\n'
			f.write(line)
		except:
			continue
	f.close()
	return
	
def write_capacity_measurements():
	devices = Devicedetails.objects.all()
	cursor = get_dict_cursor()
	count = 0
	t0 = datetime.now()
	for d in devices:
		device2 = d.deviceid.replace(':','')
		filename = settings.PROJECT_ROOT + '/summary/measurements/capacity/' + device2
		SQL = ""
		last = ""
		params = []
		params.append(d.deviceid)
		try:	
			with open(filename, 'r') as fh:
				# probably a better way to do this:
				for line in fh:
					last = line
		except:
			pass
		f = open(filename, 'a')
		if last!='':
			last=last.split('|')
			latest = datetime.fromtimestamp(int(last[0])/1000)
			params.append(latest)
			SQL = "SELECT \
			m_capacity.eventstamp, average, direction \
			FROM m_capacity JOIN devicedetails on devicedetails.deviceid=m_capacity.deviceid \
			WHERE m_capacity.deviceid=%s AND m_capacity.eventstamp>%s"
		else:
			SQL = "SELECT \
				m_capacity.eventstamp, average, direction \
				FROM m_capacity JOIN devicedetails on devicedetails.deviceid=m_capacity.deviceid \
				WHERE m_capacity.deviceid=%s"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		records = sorted(records,key=lambda x: datetime_helper.datetime_to_JSON(x['eventstamp']))
		for r in records:
			eventstamp = datetime_helper.datetime_to_JSON(r['eventstamp'])
			avg = r['average']
			direction = r['direction']
			if direction=='' or direction==None:
				continue
			line = str(eventstamp) + '|' + str(avg) + '|' + direction + '\n'
			f.write(line)
		f.close()
	cursor.close()
	return
	
def dump_all_latencies():
	cursor = get_dict_cursor()
	servers = IpResolver.objects.all()
	for s in servers:
		filename = settings.PROJECT_ROOT + '/summary/measurements/server_averages/' + str(s.ip)
		f = open(filename, 'w')
		params = []
		params.append(s.ip)
		SQL =  "SELECT \
				country_code AS country, \
				m_rtt.eventstamp::date AS day, \
				count(distinct m_rtt.srcip) AS ndevices, \
				count(*) AS nmeasurements, \
				avg(m_rtt.average) AS latency \
				FROM m_rtt \
				JOIN devicedetails AS d ON d.ip = m_rtt.srcip \
				WHERE m_rtt.dstip = %s AND m_rtt.average>0 AND m_rtt.average<3000 AND country_code!=''  \
				GROUP BY day, d.country_code;"
		cursor.execute(SQL,params)
		records = cursor.fetchall()
		for r in records:
			avg = r['latency']
			m_count = r['nmeasurements']
			day = datetime_helper.datetime_to_JSON(r['day'])
			country = r['country']
			d_count = r['ndevices']
			line = str(avg) + '|' + str(m_count) + '|' + str(day) + '|' + country.encode('utf-8') + '|' + str(d_count) + '\n'
			f.write(line)
		f.close()
	cursor.close()
	return
	
def write_country_count():
	filename = settings.PROJECT_ROOT + '/summary/device_data/country_count'
	countries = Devicedetails.objects.all().distinct('geoip_country').exclude(geoip_country='').values('geoip_country')
	file = open(filename, 'w')
	earliest=datetime_helper.get_daterange_start(7)
	cursor = get_dict_cursor()
	for c in countries:
		params=[]
		params.append(c['geoip_country'])
		SQL1 = "SELECT \
			COUNT(*) as d_count \
			FROM devicedetails \
			WHERE geoip_country=%s;"
		SQL2 = "SELECT \
			COUNT(DISTINCT devicedetails.deviceid) as a_count \
			FROM devicedetails join m_bitrate on devicedetails.deviceid=m_bitrate.deviceid \
			WHERE geoip_country=%s AND m_bitrate.eventstamp>%s;"
		cursor.execute(SQL1,params)
		rec = cursor.fetchone()
		device_count = rec['d_count']
		params.append(earliest)
		cursor.execute(SQL2,params)
		rec = cursor.fetchone()
		active_count = rec['a_count']
		line = c['geoip_country'].encode('utf-8') + '|' + str(device_count) + '|' + str(active_count) + '\n'
		file.write(line)
	cursor.close()
	file.close()
	return

def write_city_count():
	filename = settings.PROJECT_ROOT + '/summary/device_data/city_count'
	devices = Devicedetails.objects.all().distinct('geoip_city').exclude(geoip_city='')
	file = open(filename, 'w')
	earliest=datetime_helper.get_daterange_start(7)
	cursor = get_dict_cursor()
	for d in devices:
		if d.geoip_city==None or d.geoip_country==None or d.geoip_country=='':
			continue
		params=[]
		params.append(d.geoip_city)
		SQL1 = "SELECT \
			COUNT(*) as d_count \
			FROM devicedetails \
			WHERE geoip_city=%s;"
		SQL2 = "SELECT \
			COUNT(DISTINCT devicedetails.deviceid) as a_count \
			FROM devicedetails join m_bitrate on devicedetails.deviceid=m_bitrate.deviceid \
			WHERE geoip_city=%s AND m_bitrate.eventstamp>%s;"
		cursor.execute(SQL1,params)
		rec = cursor.fetchone()
		device_count = rec['d_count']
		params.append(earliest)
		cursor.execute(SQL2,params)
		rec = cursor.fetchone()
		active_count = rec['a_count']
		line = d.geoip_city.encode('utf-8') + '|' + d.geoip_country.encode('utf-8') + '|' + str(device_count) + '|' + str(active_count) + '\n'
		file.write(line)
	cursor.close()
	file.close()
	return

def write_isp_count():
	filename = settings.PROJECT_ROOT + '/summary/device_data/isp_count'
	isps = Devicedetails.objects.all().distinct('geoip_isp').exclude(geoip_isp='').values('geoip_isp')
	file = open(filename, 'w')
	earliest=datetime_helper.get_daterange_start(7)
	cursor = get_dict_cursor()
	for isp in isps:
		params=[]
		params.append(isp['geoip_isp'])
		SQL1 = "SELECT \
			COUNT(*) as d_count \
			FROM devicedetails \
			WHERE geoip_isp=%s;"
		SQL2 = "SELECT \
			COUNT(DISTINCT devicedetails.deviceid) as a_count \
			FROM devicedetails join m_bitrate on devicedetails.deviceid=m_bitrate.deviceid \
			WHERE geoip_isp=%s AND m_bitrate.eventstamp>%s;"
		cursor.execute(SQL1,params)
		rec = cursor.fetchone()
		device_count = rec['d_count']
		params.append(earliest)
		cursor.execute(SQL2,params)
		rec = cursor.fetchone()
		active_count = rec['a_count']
		line = isp['geoip_isp'].encode('utf-8') + '|' + str(device_count) + '|' + str(active_count) + '\n'
		file.write(line)
	cursor.close()
	file.close()
	return
	
def get_dict_cursor():
    conn_string = "host='" + settings.DATABASES['default']['HOST'] + \
                   "' dbname='" + settings.DATABASES['default']['NAME'] + \
                   "' user='" + settings.DATABASES['default']['USER'] + \
                   "' password='" + settings.DATABASES['default']['PASSWORD'] + "'";
                   
    conn = psycopg2.connect(conn_string)
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	