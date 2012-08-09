from django.http import HttpResponse, HttpResponseRedirect
from time import time,mktime,strftime
import datetime_helper
from datetime import datetime, timedelta

def linegraph_bucket(data,bucket_size,title):
	result={}
	result['name'] = title
	result['type'] = "spline"
	output=[]

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
					temp=[]
					temp.append(datetime_helper.datetime_to_JSON(measure.eventstamp))
					temp.append(int(mean))
					output.append(temp)
					
					
			   	bucket = []
				
			   	while(time>end_time):
			
			   		start_time = end_time+1;
			   		end_time = start_time+bucket_size
								  
			   		bucket.append(int(measure.average))

		n = len(bucket)
		if n!=0:
			mean = sum(bucket) / n
			temp=[]
			temp.append(datetime_helper.datetime_to_JSON(measure.eventstamp))
			temp.append(int(mean))
			output.append(temp)

		result['data']=output
	except:
		 return result

	return result

def linegraph_normal(data,title):
	return linegraph_normal(data,title,1)
	
def linegraph_normal(data,title,factor,roundit):
    output = []
    for measure in data:
        if measure.average > 0:
            output.append(
                    (datetime_helper.datetime_to_JSON(measure.eventstamp),
                     float(measure.average) * factor))
    return dict(name=title, type='line', data=output)
	
def linegraph_compare(data,title,factor,roundit,line_width):
	output = []
	result = []
	average = []
	total = 0
	for measure in data:
		if measure.average > 0:
			total += measure.average*factor
			output.append((datetime_helper.datetime_to_JSON(measure.eventstamp),float(measure.average) * factor))
	avg = 0
	if len(data)!=0:
		avg = (total/len(data))
	average.append(avg)
	result.append(dict(name=title, type='column', data=average))
	result.append(dict(name=title, type='line',data=output))
	return result


def linegraph_normal_passive(data,title):
    result={}
    result['name'] = title
    result['type'] = "column"
    output= []
   
    for measure in data:

	if(measure.bytes_transferred <= 0):
		continue
	temp=[]
	
	temp.append(datetime_helper.datetime_to_JSON(measure.eventstamp))
	temp.append(int(measure.bytes_transferred))
	output.append(temp)

    result['data'] = output
    return result
	



