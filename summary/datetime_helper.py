from calendar import timegm
from datetime import datetime

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