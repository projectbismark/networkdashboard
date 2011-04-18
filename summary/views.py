# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from dashboard.summary.models import *

def index(request):
    return render_to_response('index.html')

def showdevices(request):
    device_list = Devices.objects.all()
    return render_to_response('devices.html', {'device_list': device_list})

def devicesummary(request, device):
    device_details = Devices.objects.filter(deviceid=device)
    return render_to_response('device.html', {'device_details': device_details})
    return HttpResponse(output)
