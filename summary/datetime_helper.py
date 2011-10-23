from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, timedelta
from time import time,mktime,strftime
from mx.DateTime.ISO import ParseDateTimeUTC


def mmddYY_to_datetime_format(time):
    s = str(time)
    s2 = datetime.strptime(s,"%Y-%m-%d %H:%M:%S")
    s3 = ParseDateTimeUTC(str(s2))
    s4 = datetime.fromtimestamp(s3)  
    return s4

def datetime_to_JSON(time):
    x = datetime.fromtimestamp(mktime(time.timetuple()))
    return "Date.UTC(" + str(x.year) + "," +str(x.month) + "," +str(x.day) + "," +str(x.hour) + "," +str(x.minute) + "," +str(x.second) + "," +str(x.microsecond/1000)+")"

def datetime_format_to_unixtime(time):
    return mktime(time.timetuple())

def unixtime_to_datetime_format(time):
    return datetime.fromtimestamp(time)

