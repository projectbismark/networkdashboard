from django.core.management.base import NoArgsCommand
from networkdashboard.summary import database_helper
from networkdashboard.summary.models import *
import os
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
		all_devices = Devicedetails.objects.all().values('deviceid')
		device_list = []
		for device in all_devices:
			device_list.append(device['deviceid'])
		for device in device_list:
			database_helper.update_bitrate(device)
			database_helper.update_rtt(device)
			database_helper.update_lmrtt(device)
			database_helper.update_shaperate(device)
			database_helper.update_capacity(device)
			database_helper.update_unload(device)
		lock.release()
	return
