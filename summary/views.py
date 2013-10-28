import views_helper
import data_helper
import database_helper
import datetime_helper
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import Template, Context
from django.utils import simplejson
import geoip_helper
import json
from networkdashboard.summary.models import *
import psycopg2
import site
from time import time,mktime,strftime
import urllib2
import urllib
from django.db import connection
import decimal

site.addsitedir("/home/abhishek/.local/lib/python2.6/site-packages/")

def index(request):
	countries = views_helper.get_sorted_country_data()
	cities = views_helper.get_sorted_city_data()
	isps = views_helper.get_sorted_isp_data()
	device_count = data_helper.get_device_count()
	active_count = data_helper.get_active_count()
	return render_to_response('index.html', {'country_data' : countries, 'city_data': cities, 'isp_data': isps, 'device_count':device_count, 'active_count':active_count})
	
def compare_by_city(request, city, country):
	#default daterange is last 7 days:
	end_date=datetime.now()
	start_date=datetime_helper.get_daterange_start(7)
	start_day=start_date.day
	start_month=start_date.month
	start_year=start_date.year
	end_day=end_date.day
	end_month=end_date.month
	end_year=end_date.year
	return render_to_response('compare_by_city.html', {'city' : city, 'country' : country, 'start_day' : start_day, 'start_month' : start_month, 'start_year' : start_year, 'end_day' : end_day, 'end_month' : end_month, 'end_year' : end_year})
	
def compare_by_country(request, country):
	#default daterange is last 7 days:
	end_date=datetime.now()
	start_date=datetime_helper.get_daterange_start(7)
	start_day=start_date.day
	start_month=start_date.month
	start_year=start_date.year
	end_day=end_date.day
	end_month=end_date.month
	end_year=end_date.year
	return render_to_response('compare_by_country.html', {'country' : country, 'start_day' : start_day, 'start_month' : start_month, 'start_year' : start_year, 'end_day' : end_day, 'end_month' : end_month, 'end_year' : end_year})
	
def compare_by_isp(request, isp, country):
	end_date=datetime.now()
	#default daterange is 7 days:
	start_date=datetime_helper.get_daterange_start(7)
	start_day=start_date.day
	start_month=start_date.month
	start_year=start_date.year
	end_day=end_date.day
	end_month=end_date.month
	end_year=end_date.year
	return render_to_response('compare_by_isp.html', {'isp' : isp, 'country' : country, 'city' : 'none', 'start_day' : start_day, 'start_month' : start_month, 'start_year' : start_year, 'end_day' : end_day, 'end_month' : end_month, 'end_year' : end_year})
	
def compare_by_isp_and_city(request, isp, city):
	country = geoip_helper.get_country_by_city(city)
	end_date=datetime.now()
	#default daterange is 7 days:
	start_date=datetime_helper.get_daterange_start(7)
	start_day=start_date.day
	start_month=start_date.month
	start_year=start_date.year
	end_day=end_date.day
	end_month=end_date.month
	end_year=end_date.year
	return render_to_response('compare_by_isp.html', {'isp' : isp, 'country' : country, 'city' : city, 'start_day' : start_day, 'start_month' : start_month, 'start_year' : start_year, 'end_day' : end_day, 'end_month' : end_month, 'end_year' : end_year})

#returns line series data representing bitrates for a number of devices in a particular city:	
def compare_line_bitrate_by_city(request):
	#for limiting number of line series:
	max_results = int(request.GET.get('max_results'))
	start = request.GET.get('start')
	end = request.GET.get('end')
	city = request.GET.get('city')
	direction = request.GET.get('direction')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	series = views_helper.compare_line_bitrate_by_city(max_results,city,direction,earliest,latest)
	return HttpResponse(json.dumps(series))
	
#returns column series data representing bitrate measurements averaged by ISP for a particular city:	
def compare_bar_bitrate_by_city(request):
	start = request.GET.get('start')
	end = request.GET.get('end')
	city = request.GET.get('city')
	direction = request.GET.get('direction')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	bar_series= data_helper.parse_bitrate_city_average(earliest,latest,city,direction)
	return HttpResponse(json.dumps(bar_series))

#returns column series data representing bitrate measurements averaged by ISP for a particular country:	
def compare_bitrate_by_country(request):
	start = request.GET.get('start')
	end = request.GET.get('end')
	country = request.GET.get('country')
	direction = request.GET.get('direction')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	series= data_helper.parse_bitrate_country_average(earliest,latest,country,direction)
	return HttpResponse(json.dumps(series))

#returns line series data representing bitrates for a number of devices for a particular ISP
def compare_line_bitrate_by_isp(request):	
	#for limiting number of line series:
	max_results = int(request.GET.get('max_results'))
	start = request.GET.get('start')
	end = request.GET.get('end')
	isp = request.GET.get('isp')
	country = request.GET.get('country')
	direction = request.GET.get('direction')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	series = views_helper.compare_line_bitrate_by_isp(max_results,isp,country,direction,earliest,latest)
	return HttpResponse(json.dumps(series))

#returns column series data representing bitrate measurements averaged for a particular isp:
def compare_bar_bitrate_by_isp(request):	
	start = request.GET.get('start')
	end = request.GET.get('end')
	isp = request.GET.get('isp')
	country = request.GET.get('country')
	direction = request.GET.get('direction')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	bar_series = data_helper.parse_bitrate_isp_average(earliest,latest,isp,direction,country)
	return HttpResponse(json.dumps(bar_series))

#returns line series data representing lmrtt measurements averaged by ISP for a particular city
def compare_line_lmrtt_by_city(request):
	#for limiting number of line series:
	max_results = int(request.GET.get('max_results'))
	start = request.GET.get('start')
	end = request.GET.get('end')
	city = request.GET.get('city')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	series = views_helper.compare_line_lmrtt_by_city(max_results, city, earliest, latest)
	return HttpResponse(json.dumps(series))

#returns column series data representing average LMRTT measurements for devices in a particular city
def compare_bar_lmrtt_by_city(request):
	start = request.GET.get('start')
	end = request.GET.get('end')
	city = request.GET.get('city')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	bar_series= data_helper.parse_lmrtt_city_average(earliest,latest,city)
	return HttpResponse(json.dumps(bar_series))	

#returns column series data representing LMRTT averages for devices in a particular country:	
def compare_lmrtt_by_country(request):
	start = request.GET.get('start')
	end = request.GET.get('end')
	country = request.GET.get('country')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	bar_series= data_helper.parse_lmrtt_country_average(earliest,latest,country)
	return HttpResponse(json.dumps(bar_series))	

#returns line series data representing RTT measurements for devices in a particular city:	
def compare_line_rtt_by_city(request):	
	#for limiting number of line series:
	max_results = int(request.GET.get('max_results'))
	start = request.GET.get('start')
	end = request.GET.get('end')
	city = request.GET.get('city')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	series = views_helper.compare_line_rtt_by_city(max_results,city,earliest,latest)
	return HttpResponse(json.dumps(series))

#returns bar series data representing average RTT by ISP for devices in a particular city:
def compare_bar_rtt_by_city(request):	
	start = request.GET.get('start')
	end = request.GET.get('end')
	city = request.GET.get('city')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	bar_series= data_helper.parse_rtt_city_average(earliest,latest,city)
	return HttpResponse(json.dumps(bar_series))

#returns line series data representing LMRTT measurements for devices under a particular isp:	
def compare_line_lmrtt_by_isp(request):	
	#for limiting number of line series:
	max_results = int(request.GET.get('max_results'))
	start = request.GET.get('start')
	end = request.GET.get('end')
	isp = request.GET.get('isp')
	country = request.GET.get('country')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	series = views_helper.compare_line_lmrtt_by_isp(max_results,isp,country,earliest,latest)
	return HttpResponse(json.dumps(series))

#returns column series data representing LMRTT averages for devices under a particular isp:
def compare_bar_lmrtt_by_isp(request):	
	start = request.GET.get('start')
	end = request.GET.get('end')
	isp = request.GET.get('isp')
	country = request.GET.get('country')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	bar_series= data_helper.parse_lmrtt_isp_average(earliest,latest,isp,country)
	return HttpResponse(json.dumps(bar_series))	

#returns column series data representing RTT averages for devices in a given country:
def compare_rtt_by_country(request):
	start = request.GET.get('start')
	end = request.GET.get('end')
	country = request.GET.get('country')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	bar_series= data_helper.parse_rtt_country_average(earliest,latest,country)
	return HttpResponse(json.dumps(bar_series))

#returns line series data representing RTT measurements for devices under a particular isp:	
def compare_line_rtt_by_isp(request):	
	#for limiting number of line series:
	max_results = int(request.GET.get('max_results'))
	start = request.GET.get('start')
	end = request.GET.get('end')
	isp = request.GET.get('isp')
	country = request.GET.get('country')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	series = views_helper.compare_line_rtt_by_isp(max_results,isp,country,earliest,latest)
	return HttpResponse(json.dumps(series))

#returns column series data representing RTT averages for devices under a particular isp:	
def compare_bar_rtt_by_isp(request):	
	start = request.GET.get('start')
	end = request.GET.get('end')
	isp = request.GET.get('isp')
	country = request.GET.get('country')
	earliest = datetime_helper.format_date_from_calendar(start)
	latest = datetime_helper.format_date_from_calendar(end)
	bar_series= data_helper.parse_rtt_isp_average(earliest,latest,isp,country)
	return HttpResponse(json.dumps(bar_series))	

#part of API which allows limited querying through a URL.
#returns rtt measurements for a device in JSON format: 
def rtt_json(request,device,dstip,days):
	result = database_helper.get_rtt_measurements(device, days, dstip)
	return HttpResponse(json.dumps(result))

#part of API which allows limited querying through a URL.
#returns LMRTT measurements for a device in JSON format: 
def lmrtt_json(request,device,days):
	result = database_helper.get_lmrtt_measurements(device,days)
	return HttpResponse(json.dumps(result))

#part of API which allows limited querying through a URL.
#returns bitrate measurements for a device in JSON format: 	
def bitrate_json(request,device,direction,days,multi):
	result = database_helper.get_bitrate_measurements(device,days,direction,multi)
	return HttpResponse(json.dumps(result))

#returns a webpage where a user may edit the details of the user's own device
def edit_device_page(request, devicehash):
	device_details = database_helper.get_details_by_hash(devicehash)
	if len(device_details) < 1:
		return render_to_response('device_not_found.html', {'devicename' : devicehash})
	device = str(device_details[0].deviceid)
	return render_to_response('edit_device.html', {'detail' : device_details[0], 'deviceid': device})
  
#returns coordinates in JSON format for the device map:  
def get_coordinates(request):
	result = data_helper.parse_coords()
	return HttpResponse(json.dumps(result))
        
#returns a shared device summary page, a device page that may not be edited by the viewer:
def shared_device_summary(request,devicehash):
    device_details = database_helper.get_details_by_hash(devicehash)
    if len(device_details)>0:
		device = device_details[0].deviceid		
    else:
		return render_to_response('device_not_found.html', {'deviceid': devicehash})
    return views_helper.get_response_for_shared_device(device_details[0])

#returns a device summary page for the user's own device
def device_summary(request):
	device = str(request.POST.get('device'))
	device_details = database_helper.get_details_by_deviceid(device)
	try:
		#if this device page does not exist, attempt to create one:
		if device_details.count()==0:
			valid_device = database_helper.save_device_details_from_default(device)
			if valid_device:
				device_details = Devicedetails.objects.filter(deviceid=device)
			#failure usually is the result of an invalid mac address string
			else:
				return render_to_response('invalid_device.html', {'deviceid': device})
	except:
		return render_to_response('invalid_device.html', {'deviceid': device})
	#following a device edit:
	if(request.POST.get('edit')):
		try:
			database_helper.save_device_details_from_request(request,device)
		except:
			return render_to_response('invalid_edit.html', {'deviceid' : hashing})
	hashing = device_details[0].hashkey
	if (hashing==''):
		database_helper.assign_hash(device)
		device_details = database_helper.get_details_by_deviceid(device)
	return views_helper.get_response_for_devicehtml(device_details[0])

#returns a string representing the city and country for a device, as set by the user
def get_location(request, device):   
    return HttpResponse(views_helper.get_location(device))
	
#returns series data in highstock format (JSON):
def linegraph_rtt(request):
	device = request.GET.get('deviceid')
	data = data_helper.parse_rtt_measurements(device)
	return HttpResponse(json.dumps(data))

#returns series data in highstock format (JSON):	
def linegraph_unload(request):
	device = request.GET.get('deviceid')
	data = data_helper.parse_underload_measurements(device)
	return HttpResponse(json.dumps(data))
	
#returns series data in highstock format (JSON):
def linegraph_bitrate(request):
	device = request.GET.get('deviceid')
	graphno = int(request.GET.get('graphno'))
	if graphno==1:
		data = data_helper.parse_bitrate_measurements(device,'dw')
	else:
		data = data_helper.parse_bitrate_measurements(device,'up')
	return HttpResponse(json.dumps(data))

#returns series data in highstock format (JSON):
def linegraph_lmrtt(request):
	device = request.GET.get('deviceid')
	data = data_helper.parse_lmrtt_measurements(device)
	return HttpResponse(json.dumps(data))

#returns series data in highstock format (JSON):
def linegraph_shaperate(request):
	device = request.GET.get('deviceid')
	data = []
	shaperate_series = data_helper.parse_shaperate_measurements(device)
	capacity_series = data_helper.parse_capacity_measurements(device)
	for s in shaperate_series:
		data.append(s)
	for s in capacity_series:
		data.append(s)
	return HttpResponse(json.dumps(data))

#returns country RTT visualization page
def countries_vis(request):
	server_list = database_helper.get_server_list()
	end_date=datetime.now()
	start_date=datetime_helper.get_daterange_start(31)
	start_day=start_date.day
	start_month=start_date.month
	start_year=start_date.year
	end_day=end_date.day
	end_month=end_date.month
	end_year=end_date.year
	return render_to_response('countries_vis.html', {'server_list': server_list, 'start_day':start_day,'start_month':start_month,'start_year':start_year,'end_day':end_day,'end_month':end_month,'end_year':end_year});

#returns latency averages to countries_vis.html
def get_countries_vis_data(request):
	start_date = request.GET.get('startdate')
	end_date = request.GET.get('enddate')
	start_date = datetime_helper.format_date_from_calendar(start_date)
	end_date = datetime_helper.format_date_from_calendar(end_date)
	start = int(datetime_helper.datetime_to_JSON(start_date))
	end = int(datetime_helper.datetime_to_JSON(end_date))
	server = request.GET.get('serverip')
	data = data_helper.parse_countries_vis_data(start,end,server)
	return HttpResponse(json.dumps(data))

'''
80	80	Web
443	443	HTTPSs
993	993	IMAPS
587	587	SMTPS
995	995	POP3S
5223	5223	JABBER
53	53	DNS
25	25	SMTP
22	22	SSH
'''
