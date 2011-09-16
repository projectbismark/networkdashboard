# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
from pyofc2 import *
import random
from datetime import datetime, timedelta
from time import time,mktime,strftime
from mx.DateTime.ISO import ParseDateTimeUTC

def index(request):
    return render_to_response('index.html')

def editDevicePage(request, device):
    device_details = Devicedetails.objects.filter(deviceid=device)
    if len(device_details) < 1:
	device_entry = Devicedetails(deviceid = device,  eventstamp = datetime.now())
    else:
	device_entry = device_details[0]
    
    isp_options = ["Comcast","Verizon","At&t"]
    isp_options.sort()
    country_options = ['United States','South Africa','France']
    country_options.sort()
    
    return render_to_response('edit_device.html', {'detail' : device_details[0], 'deviceid': device, 'isp_options': isp_options, 'country_options': country_options})

def invalidEdit(request, device):
    return render_to_response('invalid_edit.html', {'deviceid' : device})

def newuser(request):
    return render_to_response('newuser.html')

def submitchanges(request, device, isp, loc, serv, dr, ur):
    return
    
 
def showdevices(request):
    device_list = Devices.objects.all()
    thelist = list()
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

def devicesummary(request):
    device = request.POST.get("device")
    if(request.POST.get("edit")):
        try:
            dname = request.POST.get('name')
            disp = request.POST.get('isp')
            dlocation = request.POST.get('location')
            dsp = request.POST.get('sp')
            durate = int(request.POST.get('urate'))
            ddrate = int(request.POST.get('drate'))
            dcity = request.POST.get('city')
            dstate = request.POST.get('state')
            dcountry = request.POST.get('country')           
            details = Devicedetails(deviceid = device, name = dname, isp = disp, serviceplan = dsp, city = dcity, state = dstate, country = dcountry, uploadrate = durate, downloadrate = ddrate, eventstamp = datetime.now())
            details.save()
        except:
            return render_to_response('invalid_edit.html', {'deviceid' : device})


    device_details = Devicedetails.objects.filter(deviceid=device) 
    if len(device_details)<1:
        device_entry = Devicedetails(deviceid = device,  eventstamp = datetime.now())
        device_entry.save()
        device_details = Devicedetails.objects.filter(deviceid=device)
    
    try:
        device_search = MBitrate.objects.filter(deviceid=device)
        if (len(device_search)<1):
            return render_to_response('device_not_found.html', {'deviceid': device})
    except:
        return render_to_response('device_not_found.html', {'deviceid': device})
    first = MBitrate.objects.filter(deviceid=device).order_by('eventstamp')[0:3]
    first = datetime.fromtimestamp(mktime(first[0].eventstamp.timetuple())).strftime("%B %d, %Y")
    last = MBitrate.objects.filter(deviceid=device).order_by('-eventstamp')[0:3]
    
    calenderTo = datetime.fromtimestamp(mktime(last[0].eventstamp.timetuple())).strftime("%Y-%m-%d")
    calenderFrom = datetime.fromtimestamp(mktime(last[0].eventstamp.timetuple()) - 3600*24*7).strftime("%Y-%m-%d")
    last = datetime.fromtimestamp(mktime(last[0].eventstamp.timetuple())).strftime("%B %d, %Y")

    return render_to_response('device.html', {'detail': device_details[0],'firstUpdate': first, 'lastUpdate': last, 'calenderFrom': calenderFrom,'calenderTo': calenderTo, 'deviceid': device}) 

def getISP(request, device):
##    UDrow = Userdevice.objects.filter(deviceid=device)
##    if len(UDrow)==0:
##	return HttpResponse(' ')
##    print UDrow[0].userid
##    USrow = Usersla.objects.filter(userid=UDrow[0].userid)
##    if len(USrow)==0:
##	return HttpResponse(' ')
##    SLArow = Sla.objects.filter(slaid=USrow[0].slaid)
##    if len(SLArow)==0:
##	return HttpResponse(' ')
##    return HttpResponse(SLArow[0].isp)
    return HttpResponse('unavailable')

def getPlan(request, device):
##    UDrow = Userdevice.objects.filter(deviceid=device)
##    if len(UDrow)==0:
##	return HttpResponse(' ')
##    print UDrow[0].userid
##    USrow = Usersla.objects.filter(userid=UDrow[0].userid)
##    if len(USrow)==0:
##	return HttpResponse(' ')
##    SLArow = Sla.objects.filter(slaid=USrow[0].slaid)
##    if len(SLArow)==0:
##	return HttpResponse(' ')
##    return HttpResponse(SLArow[0].sla)
    return HttpResponse('unavailable')

def getUl(request, device):
##    UDrow = Userdevice.objects.filter(deviceid=device)
##    if len(UDrow)==0:
##	return HttpResponse(' ')
##    print UDrow[0].userid
##    USrow = Usersla.objects.filter(userid=UDrow[0].userid)
##    if len(USrow)==0:
##	return HttpResponse(' ')
##    SLArow = Sla.objects.filter(slaid=USrow[0].slaid)
##    if len(SLArow)==0:
##	return HttpResponse(' ')
##    return HttpResponse(SLArow[0].ul)
    return HttpResponse('unavailable')


def getDl(request, device):
##    UDrow = Userdevice.objects.filter(deviceid=device)
##    if len(UDrow)==0:
##	return HttpResponse(' ')
##    print UDrow[0].userid
##    USrow = Usersla.objects.filter(userid=UDrow[0].userid)
##    if len(USrow)==0:
##	return HttpResponse(' ')
##    SLArow = Sla.objects.filter(slaid=USrow[0].slaid)
##    if len(SLArow)==0:
##	return HttpResponse(' ')
##    return HttpResponse(SLArow[0].dl)
    return HttpResponse('unavailable')

def getLastUpdate(request, device):
    last = MBitrate.objects.filter(deviceid=device).order_by('-eventstamp')[0:3]
    if len(last)>0:
        end = datetime.fromtimestamp(mktime(last[0].eventstamp.timetuple())).strftime("%B %d, %Y")
	return HttpResponse(end)
    
    return HttpResponse('unavailable')

def getLastUpdateYMD(request, device):
##    last = Measurements.objects.filter(deviceid=device).order_by('-timestamp')[0:3]
##    if len(last)<0:
##	return HttpResponse('not found')
##    return HttpResponse(str(datetime.fromtimestamp(last[0].timestamp).strftime("%m/%d/%y")))
    return HttpResponse('unavailable')

def getFirstUpdate(request, device):
    last = MBitrate.objects.filter(deviceid=device).order_by('eventstamp')[0:3]
    if len(last)>0:
        end = datetime.fromtimestamp(mktime(last[0].eventstamp.timetuple())).strftime("%B %d, %Y")
	return HttpResponse(end)
    
    return HttpResponse('unavailable')

def getLocation(request, device):
    details = Devicedetails.objects.filter(deviceid=device)

    if len(details)>0:
        return HttpResponse(details[0].city + ", " + details[0].country)
    
    dev = MBitrate.objects.filter(deviceid=device, srcip ='143.215.131.173' )
    if len(dev)>0:
        ip = str(dev[0].dstip)
        urlobj=urllib2.urlopen("http://api.ipinfodb.com/v3/ip-city/?key=c91c266accebc12bc7bbdd7fef4b5055c1485208bb6c20b4cc2991e67a3e3d34&ip=" + ip + "&format=json")
        r1 = urlobj.read()
        urlobj.close()
        datadict = json.loads(r1)
        print "\n" + ip
        res = datadict["cityName"] + "," + datadict["countryName"]
        return HttpResponse(res)  
    
    return HttpResponse('unavailable')

def cvs_linegraph(request):
    device = request.GET.get('deviceid')
    chosen_param = request.GET.get('param')
    chosen_limit = request.GET.get('limit')
    timetype = request.GET.get('type')
    graphno = int(request.GET.get('graphno'))
    '''
    chosen_param = 'AGGL3BITRATE'
    chosen_limit = 100000
    timetype = 0
	'''

    s = request.GET.get('start')
    s2 = datetime.strptime(s,"%m/%d/%Y")
    s3 = ParseDateTimeUTC(str(s2))
    s4 = datetime.fromtimestamp(s3)   
    start = s4
    e = request.GET.get('end')
    e2 = datetime.strptime(e,"%m/%d/%Y")
    e3 = ParseDateTimeUTC(str(e2))
    
    e4 = datetime.fromtimestamp(e3)+ timedelta(1,0)
    end = e4
    if chosen_param == 'AGGL3BITRATE' :
        device_details_down = MBitrate.objects.filter(deviceid=device,eventstamp__gt=start,eventstamp__lte=end,average__lte=chosen_limit,srcip='143.215.131.173')
        device_details_up = MBitrate.objects.filter(deviceid=device,eventstamp__gt=start,eventstamp__lte=end,average__lte=chosen_limit,dstip='143.215.131.173')
        
        tim1 = list()
        dat1 = list()
        dat2 = list()
       
        for measure in device_details_down:
            t = datetime.fromtimestamp(mktime(measure.eventstamp.timetuple()))
            tim1.append(t)
            dat1.append(str(measure.average) + ", " + str(measure.std))

        for measure in device_details_up:
            dat2.append(str(measure.average) + ", " + str(measure.std))

        xVariable = "Date"
        yVariable = "Down (kbps)"
        if(graphno==2):
            yVariable = "Up (kbps)"
            
        output = xVariable + "," + yVariable + "\n"

        if(graphno==1):
            for i in range(0,min(len(dat1),len(dat2))):
                ret = str(tim1[i]) + "," + str(dat1[i]) +"\n"
                output += ret
        elif(graphno==2):
            for i in range(0,min(len(dat1),len(dat2))):
                ret = str(tim1[i]) + "," + str(dat2[i]) + "\n"
                output += ret
        

    elif chosen_param == 'RTT' :

        distinct_ips = MRtt.objects.values('dstip').distinct()
	xVariable = "Date"
        yVariable = request.GET.get('unit')
        output = xVariable

        for row_ip in distinct_ips:
            print row_ip["dstip"]

	    urlobj=urllib2.urlopen("http://api.ipinfodb.com/v3/ip-city/?key=c91c266accebc12bc7bbdd7fef4b5055c1485208bb6c20b4cc2991e67a3e3d34&ip=" + row_ip['dstip'] + "&format=json")
	
	    r1 = urlobj.read()
	    urlobj.close()
	    datadict = json.loads(r1)
            output = output + "," + datadict['cityName']+"-" + datadict['countryCode'] + "test"
        output+="\n"
        time = list()
        data = list()
        for row_ip in distinct_ips:
            device_details = MRtt.objects.filter(deviceid=device,eventstamp__gt=start,eventstamp__lte=end,average__lte=chosen_limit, dstip = row_ip["dstip"])
            data1 = list()
            for measure in device_details:
                data1.append(str(measure.average) + ", " + str(measure.std))

            data.append(data1)
            
        device_details = MRtt.objects.filter(deviceid=device,eventstamp__gt=start,eventstamp__lte=end,average__lte=chosen_limit,dstip='143.215.131.173')
        for row_details in device_details:
            time.append(row_details.eventstamp)

        for i in range(0,len(time)):
            ret = str(time[i])

            for temp in data:
                if i>=len(temp):
                    continue
                ret += "," + str(temp[i])

            ret+="\n"
            output += ret
        

    elif chosen_param == 'LMRTT' :

    
        device_details = MLmrtt.objects.filter(deviceid=device,eventstamp__gt=start,eventstamp__lte=end,average__lte=chosen_limit)
        xVariable = "Date"
        yVariable = request.GET.get('unit')
        output = xVariable + "," + yVariable +"\n"
        for measure in device_details:
            t = measure.eventstamp
            ret = str(t) + "," + str(measure.average) + ", " + str(measure.std) + "\n"
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

