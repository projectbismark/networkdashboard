from django.http import HttpResponse, HttpResponseRedirect
from time import time,mktime,strftime
import datetime_helper
from datetime import datetime, timedelta

def linegraph_bucket(data,bucket_size,text_format,title):
	result={}
	result['name'] = title
	output="["
	is_first = True
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
					if not is_first:
						output+=',';
					else:
						is_first=False;
					output+=text_format.format(datetime_helper.datetime_to_JSON(mid_time), str(mean))
					
					
			   	bucket = []
				
			   	while(time>end_time):
			
			   		start_time = end_time+1;
			   		end_time = start_time+bucket_size
								  
			   		bucket.append(int(measure.average))

		n = len(bucket)
		if n!=0:
			mean = sum(bucket) / n
			output+=text_format.format(datetime_helper.datetime_to_JSON(mid_time), str(mean))
    		output += ']'
		result['data']=output
	except:
		 return result

	return result

def linegraph_normal(data,text_format,title):
    result={}
    result['name'] = title
    output= []

    for measure in data:

	if(measure.average <= 0):
		continue
	temp=[]
	temp.append(datetime.fromtimestamp(mktime(measure.eventstamp.timetuple())))
	temp.append(int(measure.average))
	output.append(temp)

    result['data'] = output
    return result


