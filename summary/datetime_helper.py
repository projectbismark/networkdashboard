from calendar import timegm
import datetime
from datetime import timedelta

def unix_to_date(time):
	return time.gmtime(time)

def datetime_to_JSON(time):
    return int(timegm(time.timetuple()) * 1000)

def datetime_format_to_unixtime(time):
    return timegm(time.timetuple())
	
def is_recent(last, period):
	now = datetime.datetime.now()
	delta = now - last
	if (delta.days<period):
		return True
	else:
		return False
		
def get_daterange_start(days):
	now = datetime.datetime.now()
	earliest = now - timedelta(days=days)
	return earliest
	
def format_date_from_calendar(date_string):
	# format is YYYY-MM-DD
	date = date_string.split("-")
	year = int(date[0])
	month = int(date[1])
	day = int(date[2])
	return datetime.datetime(year,month,day)
	