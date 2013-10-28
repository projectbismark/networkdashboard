from calendar import timegm
import datetime
from datetime import timedelta

def datetime_to_JSON(t):
    return int(timegm(t.timetuple()) * 1000)
		
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
	