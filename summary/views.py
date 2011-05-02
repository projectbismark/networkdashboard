# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from dashboard.summary.models import *
from pyofc2  import * 
import random


import time

def index(request):
    return render_to_response('index.html')

def showdevices(request):
    device_list = Devices.objects.all()
    return render_to_response('devices.html', {'device_list': device_list})

def devicesummary(request, device):
    device_details = Devices.objects.filter(deviceid=device)
    return render_to_response('device.html', {'device_details': device_details})
    return HttpResponse(output)

def chart_data(request):
    t = title(text=time.strftime('%a %Y %b %d'))
    l = line()
    l.values = [9,8,7,6,5,4,3,2,1]
    y = y_axis(max=max(l.values),stroke=0)
    
    chart = open_flash_chart()
    chart.title = t
    chart.y_axis = y
    chart.add_element(l)
    return HttpResponse(chart.render())

def scatter_data(request, device):
    device_details = Measurements.objects.filter(deviceid=device)[0:100]
    t = title(text=device)
    l = scatter_line()
    l.values = []

    ymax= 0
    xmin = 9999999999
    xmax = 0

    for measure in device_details:
	if measure.avg>ymax: ymax= measure.avg
	if measure.timestamp<xmin: xmin = measure.timestamp
	if measure.timestamp>xmax: xmax = measure.timestamp
	e = scatter_value(x=measure.timestamp,y=measure.avg)
	l.values.append(e)
    
    
    chart = open_flash_chart()

    y = y_axis(max=ymax,steps=(int)(ymax/10)+1)
    chart.y_axis = y
    x = x_axis(min=xmin,max=xmax,steps=(int)((xmax-xmin)/10))
    chart.x_axis = x    

    chart.title = t

    chart.add_element(l)
    return HttpResponse(chart.render())

def scatter_datamax(request, device):
    device_details = Measurements.objects.filter(deviceid=device)[0:1000]
    t = title(text=device)
    l = scatter_line()
    l.values = []

    ymax= 0
    
    xmin = 9999999999
    xmax = 2
    prevT = 0
    prevA = 0
    div = 10000
    for measure in device_details:
	if measure.avg>ymax: ymax= measure.avg
	if measure.timestamp<xmin: xmin = measure.timestamp
	if measure.timestamp>xmax: xmax = measure.timestamp
	
	if (int)(prevT/div) == (int)(measure.timestamp/div) and measure.avg>prevA:
		prevA = measure.avg

	elif (int)(prevT/div) < (int)(measure.timestamp/div):
		l.values.append(scatter_value(x=prevT,y=prevA))
		prevT = measure.timestamp
		prevA = measure.avg

    l.values.append(scatter_value(x=prevT,y=prevA))
    chart = open_flash_chart()

    y = y_axis(max=ymax,steps=(int)(ymax/10)+1)
    chart.y_axis = y
    x = x_axis(min=xmin,max=xmax,steps=(int)((xmax-xmin)/10))
    chart.x_axis = x    

    chart.title = t
    
    chart.add_element(l)
    return HttpResponse(chart.render())

