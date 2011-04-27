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
    chart = open_flash_chart()
    chart.title = t
    chart.add_element(l)
    return HttpResponse(chart.render())

def scatter_data(request):
    t = title(text=time.strftime('%a %Y %b %d'))
    l = line()
    l.values = [9,8,7,6,5,4,3,2,1]
    chart = open_flash_chart()
    chart.title = t
    chart.add_element(l)
    return HttpResponse(chart.render())

