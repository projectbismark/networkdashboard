from calendar import timegm

def datetime_to_JSON(time):
    return int(timegm(time.timetuple()) * 1000)

def datetime_format_to_unixtime(time):
    return timegm(time.timetuple())
