var filter = "none"; 

function createParameters(i){
	var graphid = 1;
	var url = "/line_bitrate/";
	var graphno = 1;
	var divid = "graph_div_1";
	var titlename ="";
	var formatter = function(){};
	var legend = {
		enabled: true,
		align: 'center',
		verticalAlign: 'top',
		borderColor: '#ddd',
		borderWidth: 1,
		shadow: false
	};
	var rangeselector={

		buttons: [{
			type: 'day',
			count: 1,
			text: '1d'
		}, {
			type: 'week',
			count: 1,
			text: '1w'
		}, {
			type: 'month',
			count: 1,
			text: '1m'
		}, {
			type: 'month',
			count: 3,
			text: '3m'
		}, {
			type: 'month',
			count: 6,
			text: '6m'
		}, {
			type: 'all',
			text: 'All'
			}],
			selected: 1
		};
		var plotoptions = {};
		var units = "Bits Per Second";


		switch (i){
			case 0:
			formatter = function(){
				var ret =Highcharts.dateFormat('%A,%e. %b %Y, %l %p', this.x) + "<br/>";
				for(var i=0;i<this.points.length;i++){
					var si = determineSI(this.points[i].y,0);
					var d = parseFloat(recDivide(this.points[i].y,this.points[i].y,0));
					ret += ''+ '<p style="color:' + this.points[i].series.color +  ';">' + this.points[i].series.name+ '</p> <b>'+ d +'</b> '+ si +' <br/>';
				}
				return ret;
			};
			graphid = 0;
			break;

			case 1:
			divid = "graph_div_2";
			graphno = 2;
			titlename = "";
			graphid = 1;
			formatter = function(){

				var ret =Highcharts.dateFormat('%A,%e. %b %Y, %l %p', this.x) + "<br/>";
				for(var i=0;i<this.points.length;i++){
					var si = determineSI(this.points[i].y,0);
					var d = parseFloat(recDivide(this.points[i].y,this.points[i].y,0));
					ret += ''+ '<p style="color:' + this.points[i].series.color +  ';">' + this.points[i].series.name+ '</p> <b>'+ d +'</b> '+ si +' <br/>';
				}
				return ret;

			};
			break;
			case 2:
			units = "Milliseconds";
			titlename = "";
			divid = "graph_div_3";
			url = "/line_rtt/";
			formatter = function(){
				var ret =Highcharts.dateFormat('%A,%e. %b %Y, %l %p', this.x) + "<br/>";
				for(var i=0;i<this.points.length;i++)
				ret += ''+ '<p style="color:' + this.points[i].series.color +  ';">' + this.points[i].series.name+ '</p> <b>'+ parseInt(this.points[i].y) +'</b> msec <br/>';
				return ret;
			}
			graphid = 2;
			break;
			case 3:
			units = "Milliseconds";
			titlename = "";
			divid = "graph_div_4";
			url = "/line_lmrtt/";
			formatter = function(){
				var ret =Highcharts.dateFormat('%A,%e. %b %Y, %l %p', this.x) + "<br/>";
				return ret+ '<p style="color:' + this.points[0].series.color +  ';">' + this.points[0].series.name+ '</p> <b>'+ parseInt(this.points[0].y) +'</b> msec';
			}
			graphid = 3;
			break;

			case 4:
			units = "Bits Per Second";
			titlename = "";
			divid = "graph_div_5";
			url = "/line_shaperate/";
			formatter = function(){
				var ret =Highcharts.dateFormat('%A,%e. %b %Y, %l %p', this.x) + "<br/>";
				var si = determineSI(this.points[0].y,0);
				var d = parseFloat(recDivide(this.points[0].y,this.points[0].y,0));
				ret += ''+ '<p style="color:' + this.points[0].series.color +  ';">' + this.points[0].series.name+ '</p> <b>'+ d +'</b> '+ si +' <br/>';
				return ret;
			};
			graphid = 3;
			break;
			case 5:
			paramselect = "PASSIVE_PORT";
			titlename = "Passive Data By Port";
			divid = "graph_div_6";
			units = "MB";
			url = "/line_passive_port/";
			formatter = function(){
				return ''+ '<p style="color:' + this.points[0].series.color +  ';">' + this.points[0].series.name+ '</p><br />'+ Highcharts.dateFormat('%A,%e. %b %Y, %l %p', this.x) +' <br/><b>'+ parseInt(this.points[0].y/1000/1000) +'</b> MB';
			};
			plotoptions ={
				column: {
					borderWidth: 0,
					stacking: "normal"
				},
				series:{
					dataGrouping:{
						groupPixelWidth: 50,
						units: [[
						'hour',
						[1]
						], [
						'day',
						[1]
						], [
						'week',
						[1]
						], [
						'month',
						[1, 3, 6]
						]]
					} 
				}

			};
			break;
		}

		var ret = {
			legend: legend,
			divid: divid,
			titlename: titlename,
			formatter: formatter,
			rangeselector: rangeselector,
			plotoptions: plotoptions,
			units: units,
			url: url,
			graphno: graphno,
			graphid: graphid
		}

		return ret;
	}


	function OnSuccessGraph(graphParams){

		return function(data){
			if(data.length>200){
				window.chart = new Highcharts.StockChart({
					chart: {
						renderTo: graphParams.divid,
					},
					legend: graphParams.legend,

					rangeSelector: graphParams.rangeselector,

					title: {
						text: graphParams.titlename
					},

					plotOptions: graphParams.plotoptions,

					xAxis: {
						maxZoom: 1 * 24 * 3600000 // fourteen days
					},
					yAxis: {
						min: 0,
						maxZoom: 10000,
						title: {
							text: graphParams.units,
							style:{
								fontSize: 15
							}
						}

					},



					tooltip: {
						formatter: graphParams.formatter
					},

					series: eval(data)
				});
			}
			else{
				var div = document.getElementById(graphParams.divid);
				div.innerHTML="<div id = 'error'><b>Insufficient Data</b></div>";
			}
			hideBar(graphParams.graphid);
		}
	}

	function renderGraphs(deviceid){
		for (var i =0; i<4; i++){
			var params = createParameters(i);
			$.ajax({
				type: "GET",
				url: params.url,
				data: {'graphno' : params.graphno, 'deviceid': deviceid, 'filter_by': filter},
				success: OnSuccessGraph(params)
			});   
		}
	}

	function determineSI(n,i){
		var d = n/1000;
		var ret = "";
		if(d<1){
			switch(i){
				case 0:
				ret = "bps";
				break;
				case 1:
				ret = "Kbps";
				break;
				case 2:
				ret = "Mbps"
				break;
				case 3:
				ret = "Gbps"
				break;
				default:
				ret = "bps"
				break;
			}
			return ret;
		}
		else{
			return determineSI(d,i+1);
		}
	}

	function recDivide(bits, n, i){
		var d = n/1000;
		if(i>3){
			return bits;
		}
		else if(d<1){
			return n;
		}
		else{
			return recDivide(bits,d,i+1);
		}
	}


