from calendar import timegm
from datetime import datetime
from datetime import timedelta

def datetime_to_JSON(time):
    return int(timegm(time.timetuple()) * 1000)

def datetime_format_to_unixtime(time):
    return timegm(time.timetuple())
	
def is_recent(last, period):
	now = datetime.now()
	delta = now - last
	if (delta.days<period):
		return True
	else:
		return False
		
def get_daterange_start(days):
	now = datetime.now()
	earliest = now - timedelta(days=days)
	return earliest
	