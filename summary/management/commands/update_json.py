from django.core.management.base import NoArgsCommand
from networkdashboard.summary import database_helper
from networkdashboard.summary.models import *
import threading

lock = threading.Lock()

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		update()
	

def update():
	t = threading.Thread(target = update_json, args = ())
	t.start()
	
def update_json():
	if(lock.acquire(False)):
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
