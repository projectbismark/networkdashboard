# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
from pyofc2 import *
import random
from datetime import datetime, timedelta
from time import time,mktime,strftime
from mx.DateTime.ISO import ParseDateTimeUTC
import hashlib
import cvs_helper,datetime_helper,database_helper,views_helper,email_helper

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

    device = str(request.POST.get("device"))
    device = device.replace(':', '')
    hashing = views_helper.get_hash(device)
    
    if(request.POST.get("edit")):
        try:
            database_helper.save_device_details_from_request(request,device)
        except:
            return render_to_response('invalid_edit.html', {'deviceid' : hashing})
     
 
    if not database_helper.fetch_deviceid_soft(device):
	if not database_helper.fetch_deviceid_hard(device):
		return render_to_response('device_not_found.html', {'deviceid': device})

       
    
    device_details = Devicedetails.objects.filter(deviceid=device)
    try: 
        if len(device_details)<1:
	    
            database_helper.save_device_details_from_default(device)
            device_details = Devicedetails.objects.filter(deviceid=device)
    except:
        return render_to_response('device_not_found.html', {'deviceid': device})

    return views_helper.get_response_for_devicehtml(device_details[0])

def getLocation(request, device):   
    return HttpResponse(database_helper.get_location(device))

def throughputGraph(request):
    device = request.GET.get('deviceid')
    graphno = int(request.GET.get('graphno'))
    filter_by = request.GET.get('filter_by')
    chosen_limit = 100000000
    data = "["
    all_device_details = MBitrate.objects.filter(average__lte = chosen_limit).order_by('eventstamp')
    if(graphno==1):
        all_device_details = all_device_details.filter(srcip = '143.215.131.173')
    else:
        all_device_details = all_device_details.filter(dstip = '143.215.131.173')
    for entry in all_device_details:
        if(data!='['):
            data+= ','
        data += '[' + datetime_helper.datetime_to_JSON(entry.eventstamp)+ ',' + str(entry.average) +"]"

    data += "]"
    return HttpResponse(data)
        
def linegraph_bitrate(request):
    device = request.GET.get('deviceid')
    graphno = int(request.GET.get('graphno'))
    filter_by = request.GET.get('filter_by')
    chosen_limit = 100000000

    details = Devicedetails.objects.filter(deviceid=device)[0]
		
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
	
    if (graphno==2):
	all_device_details = all_device_details.filter(srcip='143.215.131.173')		
    elif (graphno==1): 
        all_device_details = all_device_details.filter(dstip='143.215.131.173')

    my_device_details = all_device_details.filter(deviceid=device)
    
    my_device_details_netperf_3 = my_device_details.filter(toolid='NETPERF_3')
    my_device_details_other = my_device_details.exclude(toolid='NETPERF_3')
    result=[]
    result.append(cvs_helper.linegraph_normal(my_device_details_netperf_3,"multi"))
    result.append(cvs_helper.linegraph_normal(my_device_details_other,"single"))
	
    if (filter_by != 'none'):
	bucket_width = 24*3600
	result.append(cvs_helper.linegraph_bucket(other_device_details_netperf_3,bucket_width,"multi-median"))
	result.append(cvs_helper.linegraph_bucket(other_device_details_other,bucket_width,"single-median"))
    
    answer = str(result).replace("'D","D")
    answer = answer.replace(")'",")")


    return HttpResponse("(" + answer + ")")

def linegraph_lmrtt(request):
    device = request.GET.get('deviceid')
    filter_by = request.GET.get('filter_by')

    details = Devicedetails.objects.filter(deviceid=device)[0]

    all_device_details= MLmrtt.objects.filter(average__lte=3000).order_by('eventstamp')
    device_details = all_device_details.filter(deviceid=device)
   
    other_device_details = []
    filtered_deviceids = []	

    if (filter_by == 'location'):
	filtered_deviceids = Devicedetails.objects.filter(city=details.city).exclude(deviceid=device)

    if (filter_by == 'provider'):
	filtered_deviceids = Devicedetails.objects.filter(isp=details.isp).exclude(deviceid=device)

    for row in filtered_deviceids:
	other_device_details.extend(all_device_details.filter(deviceid=row.deviceid))
    result=[]
    result.append(cvs_helper.linegraph_normal(device_details,'last-minute Rtt'))

    if (filter_by != 'none'):
	bucket_width = 2*3600
	result.append(cvs_helper.linegraph_bucket(other_device_details,bucket_width,'median'))
    answer = str(result).replace("['","[")
    answer = answer.replace(")'",")")

    return HttpResponse("(" + answer + ")")

def linegraph_rtt(request):
    device = request.GET.get('deviceid')
    filter_by = request.GET.get('filter_by')
  
    details = Devicedetails.objects.filter(deviceid=device)[0]

    all_device_details= MRtt.objects.filter(average__lte=3000).order_by('eventstamp')

    other_device_details = []
    filtered_deviceids = []	

    if (filter_by == 'location'):
	filtered_deviceids = Devicedetails.objects.filter(city=details.city).exclude(deviceid=device)

    if (filter_by == 'provider'):
	filtered_deviceids = Devicedetails.objects.filter(isp=details.isp).exclude(deviceid=device)

    for row in filtered_deviceids:
	other_device_details.extend(all_device_details.filter(deviceid=row.deviceid))

  
    divides = {}
    
    for row in other_device_details:
	ee = str(row.dstip)
	
	if not divides.has_key(ee):
		divides[ee]=[]

	divides[ee].append(row)		
    

    distinct_ips = MRtt.objects.values('dstip').distinct()
 
    result=[]

    count = 1
    for row_ip in distinct_ips:
	try:
		ip_lookup = IpResolver.objects.filter(ip=row_ip['dstip'])[0].location
	except:
		continue
        
    	device_details = MRtt.objects.filter(deviceid=device,average__lte=3000, dstip = row_ip["dstip"])
	result.append(cvs_helper.linegraph_normal(device_details,str(ip_lookup)))

    	if (filter_by != 'none'):
		result.append(cvs_helper.linegraph_bucket(divides[str(row_ip["dstip"])],2*3600,"median"+str(count)))

	count+=1

    answer = str(result).replace("['","[")
    answer = answer.replace(")'",")")

    return HttpResponse("(" + answer + ")")

def linegraph_bytes_hour(request):
    device = request.GET.get('deviceid')
    filter_by = request.GET.get('filter_by')

    details = Devicedetails.objects.filter(deviceid=device)[0]
	
    node = database_helper.deviceid_to_nodeid(device)

    all_device_details= BytesPerHour_mem.objects.all().order_by('eventstamp')
    print node
    device_details = all_device_details.filter(node_id=node)
    print len(device_details)
    other_device_details = []
    filtered_deviceids = []	

    if (filter_by == 'location'):
	filtered_deviceids = Devicedetails.objects.filter(city=details.city).exclude(deviceid=device)

    if (filter_by == 'provider'):
	filtered_deviceids = Devicedetails.objects.filter(isp=details.isp).exclude(deviceid=device)

    for row in filtered_deviceids:
	other_device_details.extend(all_device_details.filter(deviceid=row.deviceid))
    
    result=[]
    result.append(cvs_helper.linegraph_normal_passive(device_details,'bytes per hour'))

    '''
    if (filter_by != 'none'):
	bucket_width = 2*3600
	result.append(cvs_helper.linegraph_bucket(other_device_details,bucket_width,'median'))
    '''
    answer = str(result).replace("['","[")
    answer = answer.replace(")'",")")

    return HttpResponse("(" + answer + ")")
    

def feedback(request):
	message = request.POST.get('message')
	sender = request.POST.get('sender')
	receivers = ['bismarkfeedback@gmail.com']
	try:
		email_helper.send_email(sender,receivers,message)
	except:
		return HttpResponse("fail")

	return HttpResponse("success")

	
