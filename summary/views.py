# Create your views here.

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
import urllib2, urllib, json
from django.shortcuts import render_to_response
from networkdashboard.summary.models import *
import random
import site
site.addsitedir("/home/abhishek/.local/lib/python2.6/site-packages/")
from datetime import datetime, timedelta
from time import time,mktime,strftime
#from mx.DateTime.ISO import ParseDateTimeUTC
import hashlib
import cvs_helper,datetime_helper,views_helper,email_helper,database_helper
import geoip_helper
import threading
import psycopg2
from graph_filter import *

class CompareThread(threading.Thread):
	def __init__(self,res,data,title,lineweight):
		threading.Thread.__init__(self)
		self.data = data
		self.title = title
		self.result = res
		self.lineweight = lineweight
		
	def run(self):
		res = cvs_helper.linegraph_compare(self.data,self.title,1,1,self.lineweight)
		self.result.append(res)
		
		

def index(request):
	countries = views_helper.get_sorted_country_data()
	cities = views_helper.get_sorted_city_data()
	isps = views_helper.get_sorted_isp_data()
	device_count = views_helper.get_device_count()
	return render_to_response('index.html', {'country_data' : countries, 'city_data': cities, 'isp_data': isps, 'device_count':device_count})
	
def compare(request):
	device = request.POST.get("device").strip("/")
	servers = IpResolver.objects.all()	
	return render_to_response('compare.html', {'device' : device, 'servers' : servers})
	
# def compare_rtt(request):
	# device = request.GET.get('device')
	# filter_by = request.GET.get('filter_by')
	# criteria = request.GET.get('criteria')
	# server_loc = request.GET.get('server_loc').lstrip('Latency( ').strip(')')
	# server_ip = IpResolver.objects.filter(location = server_loc)[0].ip
	# devices = views_helper.get_devices_for_compare(device,criteria)
	# max_results = int(request.GET.get('max_results'))
	# result=[]
	# threads=[]
	# result_count=0
	# for dev in devices:
		# if(result_count == max_results):
			# break
		# if dev!= device:
			# latest = MRtt.objects.filter(deviceid=dev,average__lte=3000,dstip = server_ip).order_by('-eventstamp')[:1]
			# if len(latest)!=0:
				# if (datetime_helper.is_recent(latest[0].eventstamp,10)):
					# result_count +=1
					# data = MRtt.objects.filter(deviceid=dev,average__lte=3000,dstip = server_ip).order_by('eventstamp')
					# t = CompareThread(result,data,"Other Device",2)
					# threads.append(t)
					# t.start()
	# data = MRtt.objects.filter(deviceid=device,average__lte=3000,dstip = server_ip).order_by('eventstamp')
	# t = CompareThread(result,data,"Your Device",5)
	# threads.append(t)
	# t.start()
	# for th in threads:
		# th.join()
	# return HttpResponse(json.dumps(result))
	
def compare_rtt(request):
	device = request.GET.get('device')
	filter_by = request.GET.get('filter_by')
	criteria = request.GET.get('criteria')
	server_loc = request.GET.get('server_loc').lstrip('Latency( ').strip(')')
	days = int(request.GET.get('days'))
	server_ip = IpResolver.objects.filter(location = server_loc)[0].ip
	devices = views_helper.get_devices_for_compare(device,criteria)
	max_results = int(request.GET.get('max_results'))
	earliest = datetime_helper.get_daterange_start(days)
	result = []
	result.append([])
	result.append([])
	result_count=0
	data = MRtt.objects.filter(deviceid=device,average__lte=3000,dstip = server_ip, eventstamp__gte=earliest).order_by('eventstamp')
	graph_data = cvs_helper.linegraph_compare(data,"Your Device",1,1,5)
	result[0].append(graph_data[0])
	result[1].append(graph_data[1])
	for dev in devices:
		if(result_count == max_results):
			break
		if dev!= device:
			latest = MRtt.objects.filter(deviceid=dev,average__lte=3000,dstip = server_ip).order_by('-eventstamp')[:1]
			if len(latest)!=0:
				if (datetime_helper.is_recent(latest[0].eventstamp,10)):
					data = MRtt.objects.filter(deviceid=dev,average__lte=3000,dstip = server_ip, eventstamp__gte=earliest).order_by('eventstamp')
					graph_data = cvs_helper.linegraph_compare(data,"Other Device",1,1,2)
					result[0].append(graph_data[0])
					result[1].append(graph_data[1])
					result_count +=1
	return HttpResponse(json.dumps(result))
	
# def compare_lmrtt(request):
	# deviceid = request.GET.get("device")
	# criteria = int(request.GET.get("criteria"))
	# max_results = int(request.GET.get("max_results"))
	# devices = views_helper.get_devices_for_compare(deviceid,criteria)
	# result = []
	# threads = []
	# result_count = 0
	# for dev in devices:
		# if(result_count == max_results):
			# break
		# if dev!= deviceid:
			# data= MLmrtt.objects.filter(average__lte=3000, deviceid=dev).order_by('eventstamp')
			# if len(data)!=0:
				# last = len(data) - 1
				# if (datetime_helper.is_recent(data[last].eventstamp,10)):
					# result_count += 1
					# t = CompareThread(result,data,"Other Device",2)
					# threads.append(t)
					# t.start()
	# data= MLmrtt.objects.filter(average__lte=3000, deviceid=deviceid).order_by('eventstamp')
	# t = CompareThread(result,data,"Your Device",5)
	# threads.append(t)
	# t.start()
	# for th in threads:
		# th.join()
	# return HttpResponse(json.dumps(result))
	
def compare_lmrtt(request):
	deviceid = request.GET.get("device")
	criteria = int(request.GET.get("criteria"))
	max_results = int(request.GET.get("max_results"))
	days = int(request.GET.get('days'))
	earliest = datetime_helper.get_daterange_start(days)
	devices = views_helper.get_devices_for_compare(deviceid,criteria)
	result = []
	result.append([])
	result.append([])
	result_count = 0
	data= MLmrtt.objects.filter(average__lte=3000, deviceid=deviceid, eventstamp__gte=earliest).order_by('eventstamp')
	graph_data = cvs_helper.linegraph_compare(data,"Your Device",1,1,5)
	result[0].append(graph_data[0])
	result[1].append(graph_data[1])
	for dev in devices:
		if(result_count == max_results):
			break
		if dev!= deviceid:
			data= MLmrtt.objects.filter(average__lte=3000, deviceid=dev, eventstamp__gte=earliest).order_by('eventstamp')
			if len(data)!=0:
				last = len(data) - 1
				if (datetime_helper.is_recent(data[last].eventstamp,10)):
					graph_data = cvs_helper.linegraph_compare(data,"Other Device",1,1,2)
					result[0].append(graph_data[0])
					result[1].append(graph_data[1])
					result_count += 1
	return HttpResponse(json.dumps(result))
	
# def compare_bitrate(request):
	# deviceid = request.GET.get("device")
	# criteria = int(request.GET.get("criteria"))
	# max_results = int(request.GET.get("max_results"))
	# dir = request.GET.get("direction")
	# devices = views_helper.get_devices_for_compare(deviceid,criteria)
	# result = []
	# threads = []
	# result_count = 0
	# data = MBitrate.objects.filter(deviceid = deviceid, direction = dir, toolid = 'NETPERF_3').order_by('eventstamp')
	# t = CompareThread(result,data,"Your Device",5)
	# threads.append(t)
	# t.start()
	# for dev in devices:
		# if(result_count == max_results):
			# break
		# if dev!= deviceid:
			# data = MBitrate.objects.filter(deviceid = dev, direction = dir, toolid='NETPERF_3').order_by('eventstamp')
			# if len(data)!=0:
				# last = len(data) - 1
				# if (datetime_helper.is_recent(data[last].eventstamp,10)):
					# result_count += 1
					# t = CompareThread(result,data,"Other Device",2)
					# threads.append(t)
					# t.start()
	
	# for th in threads:
		# th.join()
	# return HttpResponse(json.dumps(result))
	
def compare_bitrate(request):
	deviceid = request.GET.get("device")
	criteria = int(request.GET.get("criteria"))
	max_results = int(request.GET.get("max_results"))
	dir = request.GET.get("direction")
	days = int(request.GET.get('days'))
	devices = views_helper.get_devices_for_compare(deviceid,criteria)
	earliest = datetime_helper.get_daterange_start(days)
	result = []
	result.append([])
	result.append([])
	result_count = 0
	data = MBitrate.objects.filter(deviceid = deviceid, direction = dir, toolid = 'NETPERF_3', eventstamp__gte=earliest).order_by('eventstamp')
	graph_data = cvs_helper.linegraph_compare(data,"Your Device",1000,18000,5)
	result[0].append(graph_data[0])
	result[1].append(graph_data[1])
	for dev in devices:
		if(result_count == max_results):
			break
		if dev!= deviceid:
			data = MBitrate.objects.filter(deviceid = dev, direction = dir, toolid='NETPERF_3', eventstamp__gte=earliest).order_by('eventstamp')
			if len(data)!=0:
				last = len(data) - 1
				if (datetime_helper.is_recent(data[last].eventstamp,20)):
					graph_data = cvs_helper.linegraph_compare(data,"Other Device",1000,18000,2)
					result[0].append(graph_data[0])
					result[1].append(graph_data[1])
					result_count += 1
	return HttpResponse(json.dumps(result))

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
    return HttpResponse(geoip_helper.get_coordinates_for_googlemaps())

def getLatestInfo(request):
	devicehash = request.GET.get('devicehash')
	latestInfo = ''
    
	try:
		device_details = Devicedetails.objects.get(hashkey=devicehash)
	except Devicedetails.DoesNotExist:
		return HttpResponse('NOT AVAILABLE')

	try:
		latest_download = database_helper.get_latest_download(device_details.deviceid)
		latestInfo += 'Latest Download: ' + str(latest_download['average']) + '<br>'
	except KeyError:
		latestInfo += 'Latest Download: N/A<br>'
	try:
		latest_upload = database_helper.get_latest_upload(device_details.deviceid)
		latestInfo += 'Latest Upload: ' + str(latest_upload['average']) + '<br>'
	except KeyError:
		latestInfo += 'Latest Upload: N/A<br>'
	try:
		latest_lastmile = database_helper.get_latest_lastmile(device_details.deviceid)
		latestInfo += 'Latest Lastmile: ' + str(latest_lastmile['average']) + '<br>'
	except KeyError:
		latestInfo += 'Latest Lastmile: N/A<br>'
	try:
		latest_roundtrip = database_helper.get_latest_roundtrip(device_details.deviceid)
		latestInfo += 'Latest Roundtrip: ' + str(latest_roundtrip['average']) + '<br>'
	except KeyError:
		latestInfo += 'Latest Roundtrip: N/A<br>' 
			
	return HttpResponse(latestInfo)
        
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

def iptest(iptest):
	dat = geoip_helper.getLocation("117.192.232.202")
	return HttpResponse(str(dat))


def linegraph_bitrate(request):
	g_filter = Graph_Filter(request)
	chosen_limit = 100000000

	details = Devicedetails.objects.filter(deviceid=g_filter.device)[0]
	all_device_details= MBitrate.objects.filter(average__lte=chosen_limit).order_by('eventstamp')

	other_device_details_netperf_3 = []
	other_device_details_other = []
	filtered_deviceids = []

	if (g_filter.filter_by == 'location'):
		filtered_deviceids = Devicedetails.objects.filter(city=details.city).exclude(deviceid=g_filter.device)

	if (g_filter.filter_by == 'provider'):
		filtered_deviceids = Devicedetails.objects.filter(isp=details.isp).exclude(deviceid=g_filter.device)

	for row in filtered_deviceids:
		other_device_details_other.extend(all_device_details.filter(deviceid=row.deviceid).exclude(toolid='NETPERF_3'))
		other_device_details_netperf_3.extend(all_device_details.filter(deviceid=row.deviceid).filter(toolid='NETPERF_3'))	

	if (g_filter.graphno==1):
		all_device_details = all_device_details.filter(direction='dw')		
	elif (g_filter.graphno==2): 
		all_device_details = all_device_details.filter(direction='up')

	my_device_details = all_device_details.filter(deviceid=g_filter.device)

	my_device_details_netperf_3 = my_device_details.filter(toolid='NETPERF_3')
	my_device_details_other = my_device_details.exclude(toolid='NETPERF_3')

	result=[]
	result.append(cvs_helper.linegraph_normal(my_device_details_netperf_3,"Multi-threaded TCP",1000,18000))
	result.append(cvs_helper.linegraph_normal(my_device_details_other,"Single-threaded TCP",1000,18000))
	
	if (g_filter.filter_by != 'none'):
		bucket_width = 24*3600
		result.append(cvs_helper.linegraph_bucket(other_device_details_netperf_3,bucket_width,"multi-median"))
		result.append(cvs_helper.linegraph_bucket(other_device_details_other,bucket_width,"single-median"))


	return HttpResponse(json.dumps(result))

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
    result.append(cvs_helper.linegraph_normal(device_details,'Last mile latency',1,1))

    if (filter_by != 'none'):
		bucket_width = 2*3600
		result.append(cvs_helper.linegraph_bucket(other_device_details,bucket_width,'median'))

    return HttpResponse(json.dumps(result))

def linegraph_shaperate(request):
	device = request.GET.get('deviceid')
	filter_by = request.GET.get('filter_by')

	details = Devicedetails.objects.filter(deviceid=device)[0]

	all_device_details= MShaperate.objects.all().order_by('eventstamp')
	all_device_details_capacity= MCapacity.objects.all().order_by('eventstamp')
	device_details = all_device_details.filter(deviceid=device)
	device_details_capacity = all_device_details_capacity.filter(deviceid=device)

        device_details_up = device_details.filter(direction='up')
        device_details_dw = device_details.filter(direction='dw')
        device_details_capacity_up = device_details_capacity.filter(direction='up')
        device_details_capacity_dw = device_details_capacity.filter(direction='dw')        
		
	result=[]
	result.append(cvs_helper.linegraph_normal(device_details_up,'Shape rate Up',1000,1))
	result.append(cvs_helper.linegraph_normal(device_details_dw,'Shape rate Down',1000,1))
	result.append(cvs_helper.linegraph_normal(device_details_capacity_up,'Capacity Up',1000,1))
	result.append(cvs_helper.linegraph_normal(device_details_capacity_dw,'Capacity Down',1000,1))
	return HttpResponse(json.dumps(result))

def linegraph_rtt(request):
	
	device = request.GET.get('deviceid')
	filter_by = request.GET.get('filter_by')
    
	distinct_ips = MRtt.objects.values('dstip').distinct()
	
 	full_details = MRtt.objects.filter(deviceid=device,average__lte=3000).order_by('eventstamp')

	result=[]

	count = 1
	
	for row_ip in distinct_ips:
		try:
			ip_lookup = IpResolver.objects.filter(ip=row_ip['dstip'])[0].location	
		except:
			continue
       
		device_details = full_details.filter(dstip = row_ip["dstip"])
		
		if len(device_details)<=0 :
			continue
		
		result.append(cvs_helper.linegraph_normal(device_details,str(ip_lookup),1,1))

		if (filter_by != 'none'):
			result.append(cvs_helper.linegraph_bucket(divides[str(row_ip["dstip"])],2*3600,"median"+str(count)))
		count+=1

	return HttpResponse(json.dumps(result))

def linegraph_bytes_hour(request):
    device = request.GET.get('deviceid')
    filter_by = request.GET.get('filter_by')

    details = Devicedetails.objects.filter(deviceid=device)[0]
	
    node = database_helper.deviceid_to_nodeid(device)

    all_device_details= BytesPerHour_mem.objects.all().order_by('eventstamp')

    device_details = all_device_details.filter(node_id=node)

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

def linegraph_bytes_port_hour(request):
    device = request.GET.get('deviceid')
    filter_by = request.GET.get('filter_by')

    port_names = ['Web','HTTPS','IMAPS','SMTPS','POP3S','JABBER','DNS','SMTP','SSH']
    port_high = [80,443,993,587,995,5223,53,25,22] 
    port_low = [80,443,993,587,995,5223,53,25,22] 

    details = Devicedetails.objects.filter(deviceid=device)[0]
	
    node = database_helper.deviceid_to_nodeid(device)

    all_device_details= BytesPerPortPerHour_mem.objects.all().order_by('eventstamp')

    device_details = all_device_details.filter(node_id=node)

    other_device_details = []
    filtered_deviceids = []	

    if (filter_by == 'location'):
	filtered_deviceids = Devicedetails.objects.filter(city=details.city).exclude(deviceid=device)

    if (filter_by == 'provider'):
	filtered_deviceids = Devicedetails.objects.filter(isp=details.isp).exclude(deviceid=device)

    for row in filtered_deviceids:
	other_device_details.extend(all_device_details.filter(deviceid=row.deviceid))
    
    result=[]
    for i in range(0,len(port_names)):
    	result.append(cvs_helper.linegraph_normal_passive(device_details.filter(port=port_high[i]),port_names[i]))

    '''
    if (filter_by != 'none'):
	bucket_width = 2*3600
	result.append(cvs_helper.linegraph_bucket(other_device_details,bucket_width,'median'))
    '''
    answer = str(result).replace("['","[")
    answer = answer.replace(")'",")")

    return HttpResponse("(" + answer + ")")

  
def feedback(request):
	return render_to_response('feedback.html', {'hashkey' : request.GET.get('hashkey')})

def send_feedback(request):

	has = request.POST.get('hashkey')
	sender = request.POST.get('sender')
	message = request.POST.get('message')

	try:
		email_helper.send_email(has,sender,message)
	except:
	
		return HttpResponse("your feedback is on its way. Thank you!")
	
	return HttpResponse("feedback received. Thank you!")

'''
80	80	Web
443	443	HTTPS
993	993	IMAPS
587	587	SMTPS
995	995	POP3S
5223	5223	JABBER
53	53	DNS
25	25	SMTP
22	22	SSH
'''
