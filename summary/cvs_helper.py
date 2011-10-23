from django.http import HttpResponse, HttpResponseRedirect
from time import time,mktime,strftime
import datetime_helper
from datetime import datetime, timedelta

def linegraph_bucket(data,bucket_size,text_format):

	output=""

	try:	
		start_time = datetime_helper.datetime_format_to_unixtime(data[0].eventstamp)
		end_time = start_time + bucket_size

		bucket = []

		for measure in data:
			time = datetime_helper.datetime_format_to_unixtime(measure.eventstamp)

			if time < end_time:
				bucket.append(int(measure.average))
			else:
			   	mid_time = (start_time + end_time)/2
			   	n = len(bucket)
				if n!=0:
			   		mean = sum(bucket) / n
					output+=text_format.format(str(datetime_helper.unixtime_to_datetime_format(mid_time)), str(mean))
					
			   	bucket = []
				
			   	while(time>end_time):
			
			   		start_time = end_time+1;
			   		end_time = start_time+bucket_size
								  
			   		bucket.append(int(measure.average))

		n = len(bucket)
		if n!=0:
			mean = sum(bucket) / n
			output+=text_format.format(str(datetime_helper.unixtime_to_datetime_format(mid_time)), str(mean))

		return output
	except:
		 return ""

	return ""

