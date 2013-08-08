from django.core.management.base import NoArgsCommand
from networkdashboard.summary import database_helper
from networkdashboard.summary.models import *

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		create_devicepages()

def create_devicepages():
	# all_bitrate_devices = MBitrate.objects.values('deviceid').distinct()
	# database_helper.add_new_devices(all_bitrate_devices)
	# all_rtt_devices = MRtt.objects.values('deviceid').distinct()
	# database_helper.add_new_devices(all_rtt_devices)
	# all_lmrtt_devices = MLmrtt.objects.values('deviceid').distinct()
	# database_helper.add_new_devices(all_lmrtt_devices)
	# all_shaperate_devices = MShaperate.objects.values('deviceid').distinct()
	# database_helper.add_new_devices(all_shaperate_devices)
	# all_capacity_devices = MCapacity.objects.values('deviceid').distinct()
	# database_helper.add_new_devices(all_capacity_devices)
	database_helper.assign_hashkeys()
	return
