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
	
#priority - 1 or 0 and indicates if this series will be included in the multigraph
#id - used by multigraph to determine which metric the series represents (upload,download,rtt...)
def linegraph_normal(data,title,factor,roundit,priority,id):
    output = []
    for measure in data:
        if measure.average > 0:
            output.append(
                    (datetime_helper.datetime_to_JSON(measure.eventstamp),
                     float(measure.average) * factor))
    return dict(name=title, type='line', data=output, priority=priority, id=id)
	
# def linegraph_compare(data,title,factor,roundit,line_width):
	# output = []
	# result = []
	# average = []
	# total = 0
	# count = 0
	# for measure in data:
		# if measure.average > 0:
			# total += measure.average*factor
			# count += 1
			# output.append((datetime_helper.datetime_to_JSON(measure.eventstamp),float(measure.average) * factor))
	# avg = 0
	# if (len(data)!=0 and count!=0):
		# avg = (total/count)
	# average.append(avg)
	# result.append(dict(name=title, type='column', data=average))
	# result.append(dict(name=title, type='line',data=output))
	# return result
	
def linegraph_compare(data,title,factor,roundit,line_width):
	output = []
	for measure in data:
		if measure.average > 0:
			output.append((datetime_helper.datetime_to_JSON(measure.eventstamp),float(measure.average) * factor))
	result = dict(name=title, type='line',data=output)
	return result
	
	
def bargraph_compare(data,factor):
	result = []
	# final totals used to compute averages:
	meta_totals = []
	for d in data:
		isp = d['isp']
		new_isp = True
		for m in meta_totals:
			if m['isp'] == isp:
				new_isp = False
				m['total'] += d['total']
				m['count'] += d['count']
				m['dev_count'] += 1
				break
		if new_isp:
			new_total = {'isp' : isp, 'total' : d['total'], 'count' : d['count'], 'dev_count' : 1}
			meta_totals.append(new_total)
	for m in meta_totals:
		avg = (m['total']/m['count'])* factor
		result.append(dict(name=m['isp'], type='column', data=avg, count=m['dev_count']))
	return result
	
# computes averages for an isp with respect to city
def bargraph_compare_city(data,factor):
	result = []
	# final totals used to compute averages:
	meta_totals = []
	print len(data)
	for d in data:
		city = d['city']
		new_city = True
		for m in meta_totals:
			if m['city'] == city:
				new_city = False
				m['total'] += d['total']
				m['count'] += d['count']
				m['dev_count'] += 1
				break
		if new_city:
			new_total = {'city' : city, 'total' : d['total'], 'count' : d['count'], 'dev_count' : 1}
			meta_totals.append(new_total)
	for m in meta_totals:
		avg = (m['total']/m['count'])* factor
		result.append(dict(name=m['city'], type='column', data=avg, count=m['dev_count']))
	return result
	
# computes averages for an isp with respect to country
def bargraph_compare_country(data,factor):
	result = []
	# final totals used to compute averages:
	meta_totals = []
	for d in data:
		country = d['country']
		new_country = True
		for m in meta_totals:
			if m['country'] == country:
				new_country = False
				m['total'] += d['total']
				m['count'] += d['count']
				m['country_count'] += 1
				break
		if new_country:
			new_total = {'country' : country, 'total' : d['total'], 'count' : d['count'], 'country_count' : 1}
			print country
			meta_totals.append(new_total)
	for m in meta_totals:
		avg = (m['total']/m['count'])* factor
		result.append(dict(name=m['country'], type='column', data=avg, count=m['country_count']))
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
	



