from django.http import HttpResponse, HttpResponseRedirect
from networkdashboard.summary.models import *

def fetch_deviceid_hard(device):

	device_search = MBitrate.objects.filter(deviceid=device)[0:1]
	
	if (len(device_search)<1):
		device_search = MRtt.objects.filter(deviceid=device)[0:1]

	if (len(device_search)<1):
		device_search = MLmrtt.objects.filter(deviceid=device)[0:1]

	if (len(device_search)<1):
		return False
	else:
		return True

def list_isps():
	return ["Comcast","Time Warner Cable","At&t","Cox Optimum","Charter","Verizon","CenturyLink","SuddenLink","EarthLink","Windstream","Cable One","Frontier","NetZero Juno","Basic ISP","ISP.com","PeoplePC","AOL MSN","Fairpoint","Qwest","CableVision","MEdiaCom"]

		
		
	
