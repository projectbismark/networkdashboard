from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, timedelta
from time import time,mktime,strftime
from mx.DateTime.ISO import ParseDateTimeUTC


def mmddYY_to_datetime_format(time):
    s = time
    s2 = datetime.strptime(s,"%m/%d/%Y")
    s3 = ParseDateTimeUTC(str(s2))
    s4 = datetime.fromtimestamp(s3)  
    return s4

def datetime_format_to_unixtime(time):
    return mktime(time.timetuple())

def unixtime_to_datetime_format(time):
    return datetime.fromtimestamp(time)

