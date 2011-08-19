# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
from pyofc2 import *
import random
from datetime import datetime
from time import time,mktime
from mx.DateTime.ISO import ParseDateTimeUTC

def index(request):
    return render_to_response('index.html')

def newuser(request):
    return render_to_response('newuser.html')
 
def showdevices(request):
    device_list = Devices.objects.all()
    thelist = list()
    print 'dd'
    for row in  device_list:
	if(row.deviceid == "NB-Xuzi-Uky"):
		continue
	last = Measurements.objects.filter(deviceid=row.deviceid).order_by('-timestamp')[0:5]
	if len(last)>1:
		if time()-last[0].timestamp < 3600*24*170:
			thelist.append(row)
			print(datetime.fromtimestamp(last[0].timestamp).strftime("%Y-%m-%d %H:%M:%S"))

    return render_to_response('devices.html', {'device_list': thelist})


def showactivedevices(request):
    device_list = Devices.objects.all()
    thelist = list()
    print 'dd'
    for row in  device_list:
	if(row.deviceid == "NB-Xuzi-Uky"):
		continue
	last = Measurements.objects.filter(deviceid=row.deviceid).order_by('-timestamp')[0:5]
	if len(last)>1:
		if time()-last[0].timestamp < 3600*24*7:
			thelist.append(row)
			print(datetime.fromtimestamp(last[0].timestamp).strftime("%Y-%m-%d %H:%M:%S"))

    return render_to_response('devices.html', {'device_list': thelist})

def devicesummary(request, device):
    device_details = Devices.objects.filter(deviceid=device)
    last = Measurements.objects.filter(deviceid=device).order_by('-timestamp')[0:3]
    end = datetime.fromtimestamp(last[0].timestamp).strftime("%Y-%m-%d")
    start = datetime.fromtimestamp(last[0].timestamp - 3600*24*7).strftime("%Y-%m-%d")
	
	
    return render_to_response('device.html', {'device_details': device_details, 'calenderFrom': start,'calenderTo': end})
    return HttpResponse(output)

def getISP(request, device):
    UDrow = Userdevice.objects.filter(deviceid=device)
    if len(UDrow)==0:
	return HttpResponse(' ')
    print UDrow[0].userid
    USrow = Usersla.objects.filter(userid=UDrow[0].userid)
    if len(USrow)==0:
	return HttpResponse(' ')
    SLArow = Sla.objects.filter(slaid=USrow[0].slaid)
    if len(SLArow)==0:
	return HttpResponse(' ')
    return HttpResponse(SLArow[0].isp)

def getPlan(request, device):
    UDrow = Userdevice.objects.filter(deviceid=device)
    if len(UDrow)==0:
	return HttpResponse(' ')
    print UDrow[0].userid
    USrow = Usersla.objects.filter(userid=UDrow[0].userid)
    if len(USrow)==0:
	return HttpResponse(' ')
    SLArow = Sla.objects.filter(slaid=USrow[0].slaid)
    if len(SLArow)==0:
	return HttpResponse(' ')
    return HttpResponse(SLArow[0].sla)

def getUl(request, device):
    UDrow = Userdevice.objects.filter(deviceid=device)
    if len(UDrow)==0:
	return HttpResponse(' ')
    print UDrow[0].userid
    USrow = Usersla.objects.filter(userid=UDrow[0].userid)
    if len(USrow)==0:
	return HttpResponse(' ')
    SLArow = Sla.objects.filter(slaid=USrow[0].slaid)
    if len(SLArow)==0:
	return HttpResponse(' ')
    return HttpResponse(SLArow[0].ul)


def getDl(request, device):
    UDrow = Userdevice.objects.filter(deviceid=device)
    if len(UDrow)==0:
	return HttpResponse(' ')
    print UDrow[0].userid
    USrow = Usersla.objects.filter(userid=UDrow[0].userid)
    if len(USrow)==0:
	return HttpResponse(' ')
    SLArow = Sla.objects.filter(slaid=USrow[0].slaid)
    if len(SLArow)==0:
	return HttpResponse(' ')
    return HttpResponse(SLArow[0].dl)

def getLastUpdate(request, device):
    last = Measurements.objects.filter(deviceid=device).order_by('-timestamp')[0:3]
    if len(last)<0:
	return HttpResponse('not found')
    return HttpResponse(str(datetime.fromtimestamp(last[0].timestamp).strftime("%b %d, %Y")))


def getLastUpdateYMD(request, device):
    last = Measurements.objects.filter(deviceid=device).order_by('-timestamp')[0:3]
    if len(last)<0:
	return HttpResponse('not found')
    return HttpResponse(str(datetime.fromtimestamp(last[0].timestamp).strftime("%m/%d/%y")))

def getFirstUpdate(request, device):
    last = Measurements.objects.filter(deviceid=device)[0:3]
    if len(last)<0:
	return HttpResponse('not found')
    return HttpResponse(str(datetime.fromtimestamp(last[0].timestamp).strftime("%b %d, %Y")))

def cvs_linegraph(request, device):
    
    chosen_param = request.POST.get('param')
    chosen_limit = request.POST.get('limit')
    timetype = request.POST.get('type')
    '''
    chosen_param = 'AGGL3BITRATE'
    chosen_limit = 100000
    timetype = 0
	'''

    s = request.POST.get('start')
    s2 = datetime.strptime(s,"%m/%d/%Y")
    s3 = ParseDateTimeUTC(str(s2))
    s4 = datetime.fromtimestamp(s3)   
    start = mktime(s4.timetuple())

    e = request.POST.get('end')
    e2 = datetime.strptime(e,"%m/%d/%Y")
    e3 = ParseDateTimeUTC(str(e2))
    e4 = datetime.fromtimestamp(e3)   
    end = mktime(e4.timetuple())+24*3600 
    print start
    print end
    if chosen_param == 'AGGL3BITRATE' :
	  
	    device_details_down = Measurements.objects.filter(deviceid=device,param=chosen_param,timestamp__gt=start,timestamp__lte=end,avg__lte=chosen_limit,srcip=2413265837)
	    device_details_up = Measurements.objects.filter(deviceid=device,param=chosen_param,timestamp__gt=start,timestamp__lte=end,avg__lte=chosen_limit,dstip=2413265837)
	    
	    tim1 = list()
            dat1 = list()
            dat2 = list()
           
	    for measure in device_details_down:
		t = datetime.fromtimestamp(measure.timestamp)
		tim1.append(t)
		dat1.append(measure.avg)

	    for measure in device_details_up:
		dat2.append(measure.avg)

	    xVariable = "Date"
	    yVariable = "Down (kbps)"
	    y2Variable = "Up (kbps)"
	    output = xVariable + "," + yVariable + "," +  y2Variable +"\n"

	    for i in range(0,min(len(dat1),len(dat2))):
		ret = str(tim1[i]) + "," + str(dat1[i]) + "," + str(dat2[i]) + "\n"
		output += ret
    else:
	    device_details = Measurements.objects.filter(deviceid=device,param=chosen_param,timestamp__gt=start,timestamp__lte=end,avg__lte=chosen_limit)
	    xVariable = "Date"
	    yVariable = request.POST.get('unit')
	    output = xVariable + "," + yVariable +"\n"
	    for measure in device_details:
		t = datetime.fromtimestamp(measure.timestamp).strftime("%Y-%m-%d %H:%M:%S")
		ret = t + "," + str((measure.avg)) + "\n"
		output += ret

    return HttpResponse(output)


def pie_chart(request):
	t = title(text='Device Usage (Mbs)')
	l = pie()
	l.values = []
	l.values.append(pie_value(value=495,label='IMAPS'))
	l.values.append(pie_value(value=295,label='55005'))
	l.values.append(pie_value(value=8442,label='alternate HTTP'))
	l.values.append(pie_value(value=753,label='SSH'))
	l.values.append(pie_value(value=226,label='53108'))
	l.values.append(pie_value(value=2044,label='HTTPS'))
	l.values.append(pie_value(value=109,label='Google Talk'))
	l.values.append(pie_value(value=12180,label='HTTP'))
	l.values.append(pie_value(value=669,label='62565'))
	l.values.append(pie_value(value=1440,label='commplex-link'))
	l.values.append(pie_value(value=567,label='52552'))
	chart = open_flash_chart()
	chart.title = t
	cols = ['#d01f3c','#356aa0','#C79810']
	chart.colours=cols
	chart.add_element(l)
	return HttpResponse(chart.render())

