from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, timedelta
from time import time,mktime,strftime




def datetime_to_JSON(time):
    #x = datetime.fromtimestamp(mktime(time.timetuple()))
	unixtime = mktime(time.timetuple())+1e-6*time.microsecond
	return unixtime
    #return "Date.UTC(" + str(x.year) + "," +str(x.month-1) + "," +str(x.day) + "," +str(x.hour) + "," +str(x.minute) + "," +str(x.second) + "," +str(x.microsecond/1000)+")"

def datetime_format_to_unixtime(time):
    return mktime(time.timetuple())

def unixtime_to_datetime_format(time):
    return datetime.fromtimestamp(time)

