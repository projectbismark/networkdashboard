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
import hashlib
import cvs_helper,datetime_helper,database_helper,views_helper

def index(request):
    return render_to_response('index.html')

def editDevicePage(request, devicehash):
    device_details = Devicedetails.objects.filter(hashkey=devicehash)

    if len(device_details) < 1:
        return render_to_response('device_not_found.html', {'devicename' : devicehash})
    
    device = str(device_details[0].deviceid)
    
    isp_options = database_helper.list_isps()
    country_options = database_helper.list_countries()
    
    return render_to_response('edit_device.html', {'detail' : device_details[0], 'deviceid': device, 'isp_options': isp_options, 'country_options': country_options})

def invalidEdit(request, device):
    return render_to_response('invalid_edit.html', {'deviceid' : device})
    
def getCoordinates(request):
    return HttpResponse(database_helper.get_coordinates_for_googlemaps())
        
def sharedDeviceSummary(request,devicehash):

    device_details = Devicedetails.objects.filter(hashkey=devicehash)

    if len(device_details)>0:
	device = device_details[0].deviceid		
    else:
	return render_to_response('device_not_found.html', {'deviceid': devicehash})

    return views_helper.get_response_for_devicehtml(device_details[0])

def devicesummary(request):
    device = request.POST.get("device")
    device = device.replace(':', '')
    m = hashlib.md5()
    m.update(device)
    hashing = m.hexdigest()
	
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
                  
            details = Devicedetails(deviceid = device, name = dname, isp = disp, serviceplan = dsp, city = dcity, state = dstate, country = dcountry, uploadrate = durate, downloadrate = ddrate, eventstamp = datetime.now(),hashkey=hashing)
            details.save()
        except:
            return render_to_response('invalid_edit.html', {'deviceid' : hashing})
     
    try:
	
        if not database_helper.fetch_deviceid_hard(device):
	    print device
            return render_to_response('device_not_found.html', {'deviceid': device})
    except:
        try:
		device_details = Devicedetails.objects.filter(hashkey=device)
		if len(device_details)>0:
			device = device_details[0].deviceid		
		else:
			return render_to_response('device_not_found.html', {'deviceid': device})
	except:
		return render_to_response('device_not_found.html', {'deviceid': device})

    device_details = Devicedetails.objects.filter(deviceid=device)
    try:
    
        if len(device_details)<1:
	    m = hashlib.md5()
	    m.update(device.replace(':', ''))
	    hashing = m.hexdigest()
            device_entry = Devicedetails(deviceid = device,  eventstamp = datetime.now(),name="default name",hashkey=hashing)
            device_entry.save()
            device_details = Devicedetails.objects.filter(deviceid=device)
    except:
        return render_to_response('device_not_found.html', {'deviceid': device})

    return views_helper.get_response_for_devicehtml(device_details[0])

def getLastUpdate(request, device):
    last = MBitrate.objects.filter(deviceid=device).order_by('-eventstamp')[0:3]
    if len(last)>0:
        end = datetime.fromtimestamp(mktime(last[0].eventstamp.timetuple())).strftime("%B %d, %Y")
	return HttpResponse(end)
    
    return HttpResponse('unavailable')


def getLocation(request, device):   
    return HttpResponse(database_helper.get_location(device))

def linegraph_bitrate(request):
    device = request.GET.get('deviceid')
    graphno = int(request.GET.get('graphno'))
    filter_by = request.GET.get('filter_by')
    chosen_limit = 10000000

    details = Devicedetails.objects.filter(deviceid=device)[0]
		
    xVariable = "Date"
    yVariable = "Multi, Single, Median_Multi,Median_Single"
    output = xVariable + "," + yVariable + "\n"

    all_device_details= MBitrate.objects.filter(average__lte=chosen_limit).order_by('eventstamp')		

    other_device_details_netperf_3 = []
    other_device_details_other = []
    filtered_deviceids = []
	

    if (filter_by == 'location'):
	filtered_deviceids = Devicedetails.objects.filter(city=details.city).exclude(deviceid=device)


    if (filter_by == 'provider'):
	filtered_deviceids = Devicedetails.objects.filter(isp=details.isp).exclude(deviceid=device)


    for row in filtered_deviceids:
	other_device_details_other.extend(all_device_details.filter(deviceid=row.deviceid).exclude(toolid='NETPERF_3'))
	other_device_details_netperf_3.extend(all_device_details.filter(deviceid=row.deviceid).filter(toolid='NETPERF_3'))	
	
    if (graphno==1):
	all_device_details = all_device_details.filter(srcip='143.215.131.173')		
    elif (graphno==2): 
        all_device_details = all_device_details.filter(dstip='143.215.131.173')

    my_device_details = all_device_details.filter(deviceid=device)

    for measure in my_device_details:
	t = datetime.fromtimestamp(mktime(measure.eventstamp.timetuple()))
	if(measure.average <= 0):
		continue
	if(str(measure.toolid)=='NETPERF_3'):
		ret = str(t) + "," + str(measure.average) + ",,,"

	else:
		ret = str(t) + ",,"+ str(measure.average)+",,"

	output+=ret+"\n"
	
    if (filter_by != 'none'):
	bucket_width = 24*3600
	print "starting1"
	output+=cvs_helper.linegraph_bitrate_compare_data(other_device_details_netperf_3,bucket_width,"{0},,,{1},\n")
	output+=cvs_helper.linegraph_bitrate_compare_data(other_device_details_other,bucket_width,"{0},,,,{1}\n")
			   
    return HttpResponse(output)


def compare_cvs_linegraph(request):
    device = request.GET.get('deviceid')
    chosen_param = request.GET.get('param')
    graphno = int(request.GET.get('graphno'))
    filter_by = request.GET.get('filter_by')

    details = Devicedetails.objects.filter(deviceid=device)[0]

    output = ""
    if chosen_param == 'RTT' :

        distinct_ips = MRtt.objects.values('dstip').distinct()
	xVariable = "Date"
        yVariable = "msec"
        output = xVariable

        for row_ip in distinct_ips:
	    ip_lookup = IpResolver.objects.filter(ip=row_ip['dstip'])[0]

            output = output + "," + ip_lookup.location

        output+="\n"
        time = list()
        data = list()
        for row_ip in distinct_ips:
            device_details = MRtt.objects.filter(deviceid=device,average__lte=3000, dstip = row_ip["dstip"])
            data1 = list()
            for measure in device_details:
		if(measure.average < 0):
			continue
                data1.append(str(measure.average))

            data.append(data1)
            
        device_details = MRtt.objects.filter(deviceid=device,average__lte=3000,dstip='143.215.131.173')
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

    
        device_details = MLmrtt.objects.filter(deviceid=device,average__lte=3000)
        xVariable = "Date"
        yVariable = "msec"
        output = xVariable + "," + yVariable +"\n"
        for measure in device_details:
	    if(measure.average < 0):
	    	continue
            t = measure.eventstamp
            ret = str(t) + "," + str(measure.average) +"\n"
            output += ret

    return HttpResponse(output)

