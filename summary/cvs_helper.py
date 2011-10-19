from django.http import HttpResponse, HttpResponseRedirect

def linegraph_bitrate_compare_data(data,bucket_size):

	output=""	
	try:	
		start_time = mktime(data[0].eventstamp.timetuple())

		end_time = start_time + bucket_size
		bucket = []
		for measure in data:
			time = mktime(measure.eventstamp.timetuple())
			
			if time < end_time:
				bucket.append(int(measure.average))
			else:
			   	mid_time = (start_time + end_time)/2

			   	n = len(bucket)
				if n!=0:
			   		mean = sum(bucket) / n
					output+=  str(datetime.fromtimestamp(mid_time)) + ",,," + str(mean) + ",\n"
				  	
			   	bucket = []
				   
			   	while(time>end_time):
			   		start_time = end_time+1;
			   		end_time = start_time+bucket_size
			  
			   		bucket.append(int(measure.average))

		return output
	except:
		 return ""

	return ""

