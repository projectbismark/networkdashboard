class Graph_Filter:
	
	def __init__(self,request):
		self.device = request.GET.get('deviceid')
		self.graphno = int(request.GET.get('graphno'))
		self.filter_by = request.GET.get('filter_by')
		self.devices = request.GET.get('devicelist')
		#self.start = request.GET.get('start')
		#self.end = request.GET.get('end')