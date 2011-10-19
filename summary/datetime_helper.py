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
