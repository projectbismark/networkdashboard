from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, timedelta
from time import time,mktime,strftime

def datetime_to_JSON(time):
    return int(mktime(time.timetuple()) * 1000)

def datetime_format_to_unixtime(time):
    return mktime(time.timetuple())

def unixtime_to_datetime_format(time):
    return datetime.fromtimestamp(time)

