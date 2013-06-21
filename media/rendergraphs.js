
var filter = "none";
var ajax;
var allSeries = new Array();

function renderGraphs(deviceid){
	for (var i =0; i<6; i++){
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

var filter = "none";
var dateFormatString = '%a, %b %e, %Y at %l:%M %p';

function sortOrdinatesDescending(firstPoint, secondPoint) {
    if (firstPoint.y < secondPoint.y) {
        return 1;
    } else if (firstPoint.y > secondPoint.y) {
        return -1;
    } else {
        return 0;
    }
}

function formatBytes(bytes) {
    var magnitude = Math.log(bytes) / Math.log(10);
    var number, units;
    if (magnitude < 3) {
        number = Highcharts.numberFormat(bytes, 3);
        units = 'bps';
    } else if (magnitude < 6) {
        number = Highcharts.numberFormat(bytes / Math.pow(10, 3), 3);
        units = 'Kbps';
    } else if (magnitude < 9) {
        number = Highcharts.numberFormat(bytes / Math.pow(10, 6), 3);
        units = 'Mbps';
    } else {
        number = Highcharts.numberFormat(bytes / Math.pow(10, 9), 3);
        units = 'Gbps';
    }
    return '<b>' + number + '</b> ' + units;
}

function getUnits(bits) {
    var magnitude = Math.log(bits) / Math.log(10);
    var units;
    if (magnitude < 3) {
        units = 'bps';
    } else if (magnitude < 6) {
        units = 'Kbps';
    } else if (magnitude < 9) {
        units = 'Mbps';
    } else {
        units = 'Gbps';
    }
    return units;
}

function createParameters(i) {
    var ret = {
        legend: {
            enabled: true,
            align: 'center',
            verticalAlign: 'top',
            borderColor: '#ddd',
            borderWidth: 1,
            shadow: false
        },
        rangeSelector: {
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
        },
        plotOptions: {
            line: {
                gapSize: 5
            }
        }
    };
    switch (i) {
        case 0:
            ret.divid = 'graph_div_1';
            ret.graphid = 0;
            ret.graphno = 1;
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = '/line_bitrate/';
            break;

        case 1:
            ret.divid = 'graph_div_2';
            ret.graphid = 1;
            ret.graphno = 2;
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = "Bits Per Second";
            ret.url = "/line_bitrate/";
            break;

        case 2:
            ret.divid = "graph_div_3";
            ret.graphid = 2;
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/line_rtt/";
            break;

        case 3:
            ret.divid = "graph_div_4";
            ret.graphid = 3;
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/line_lmrtt/";
            break;

        case 4:
            ret.divid = "graph_div_5";
            ret.graphid = 4;
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = "/line_shaperate/";
            break;
		
		case 5:
			ret.divid = "graph_div_6";
            ret.graphid = 5;
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/line_unload/";
            break;
    }
    return ret;
}

function compareParameters(i) {
    var ret = {
        legend: {
            enabled: true,
            align: 'center',
            verticalAlign: 'top',
            borderColor: '#ddd',
            borderWidth: 1,
            shadow: false
        },
        rangeSelector: {
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
            }],
            selected: 1
        },
        plotOptions: {
            line: {
                gapSize: null
            }
        }
    };
	ret.divid2 = 'graph_div_7';
    switch (i) {
        case "down":
            ret.divid = 'graph_div_6';
            ret.graphid = 0;
            ret.graphno = 1;
			ret.direction = 'dw';
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = '/compare_bitrate/';
            break;

        case "up":
            ret.divid = 'graph_div_6';
            ret.graphid = 0;
            ret.graphno = 1;
			ret.direction = 'up';
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = '/compare_bitrate/';
            break;
		
		case "lm":
            ret.divid = "graph_div_6";
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/compare_lmrtt/";
            break;
			
		case "rtt":
            ret.divid = "graph_div_6";
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/compare_rtt/";
            break;
    }
    return ret;
}

function compareByCityParameters(i) {
    var ret = {
        legend: {
            enabled: true,
            align: 'center',
            verticalAlign: 'top',
            borderColor: '#ddd',
            borderWidth: 1,
            shadow: false
        },
        rangeSelector: {
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
            }],
            selected: 1
        },
        plotOptions: {
            line: {
                gapSize: null
            },
			column: {
				point: {
					events: {
						click: function(e){
							isp = e.point.name;
							country = e.point.country;
							window.location = "/compare_by_isp/" + isp + "/" + country;
							e.preventDefault()
						}
					}
				}
			}
        }
    };
	ret.divid2 = 'graph_div_7';
    switch (i) {
        case "down":
            ret.divid = 'graph_div_6';
            ret.graphid = 0;
            ret.graphno = 1;
			ret.direction = 'dw';
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = '/compare_bitrate_by_city/';
            break;

        case "up":
            ret.divid = 'graph_div_6';
            ret.graphid = 0;
            ret.graphno = 1;
			ret.direction = 'up';
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = '/compare_bitrate_by_city/';
            break;
		
		case "lm":
            ret.divid = "graph_div_6";
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/compare_lmrtt_by_city/";
            break;
			
		case "rtt":
            ret.divid = "graph_div_6";
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/compare_rtt_by_city/";
            break;
    }
    return ret;
}

function compareByCountryParameters(i) {
    var ret = {
        legend: {
            enabled: true,
            align: 'center',
            verticalAlign: 'top',
            borderColor: '#ddd',
            borderWidth: 1,
            shadow: false
        },
        rangeSelector: {
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
            }],
            selected: 1
        },
        plotOptions: {
            line: {
                gapSize: null
            },
			column: {
				point: {
					events: {
						click: function(e){
							isp = e.point.name;
							country = e.point.country;
							window.location = "/compare_by_isp/" + isp + "/" + country;
							e.preventDefault()
						}
					}
				}
			}
        }
    };
	ret.divid2 = 'graph_div_7';
    switch (i) {
        case "down":
            ret.divid = 'graph_div_6';
            ret.graphid = 0;
            ret.graphno = 1;
			ret.direction = 'dw';
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = '/compare_bitrate_by_country/';
            break;

        case "up":
            ret.divid = 'graph_div_6';
            ret.graphid = 0;
            ret.graphno = 1;
			ret.direction = 'up';
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = '/compare_bitrate_by_country/';
            break;
		
		case "lm":
            ret.divid = "graph_div_6";
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/compare_lmrtt_by_country/";
            break;
			
		case "rtt":
            ret.divid = "graph_div_6";
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/compare_rtt_by_country/";
            break;
    }
    return ret;
}

function compareByIspParameters(i, country, isp) {
    var ret = {
        legend: {
            enabled: true,
            align: 'center',
            verticalAlign: 'top',
            borderColor: '#ddd',
            borderWidth: 1,
            shadow: false
        },
        rangeSelector: {
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
            }],
            selected: 1
        },
        plotOptions: {
            line: {
                gapSize: null
            },
			column: {
				point: {
					events: {
						click: function(e){
							if (country=="none"){
								city = e.point.name;
								window.location = "/compare_by_isp_and_city/" + isp + "/" + city;
								e.preventDefault()
							}
							else {
								return
							}
						}
					}
				}
			}
        }
    };
	ret.divid2 = 'graph_div_7';
    switch (i) {
        case "down":
            ret.divid = 'graph_div_6';
            ret.graphid = 0;
            ret.graphno = 1;
			ret.direction = 'dw';
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = '/compare_bitrate_by_isp/';
            break;

        case "up":
            ret.divid = 'graph_div_6';
            ret.graphid = 0;
            ret.graphno = 1;
			ret.direction = 'up';
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bits Per Second';
            ret.url = '/compare_bitrate_by_isp/';
            break;
		
		case "lm":
            ret.divid = "graph_div_6";
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/compare_lmrtt_by_isp/";
            break;
			
		case "rtt":
            ret.divid = "graph_div_6";
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(i, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
                });
                return ret;
            };
            ret.units = "Milliseconds";
            ret.url = "/compare_rtt_by_isp/";
            break;
    }
    return ret;
}

function onSuccessGraph(graphParams) {
    return function(data) {
        if (data.length > 200) {
            window.chart = new Highcharts.StockChart({
                chart: {
                    renderTo: graphParams.divid,
                },
                legend: graphParams.legend,
                rangeSelector: graphParams.rangeSelector,
                plotOptions: graphParams.plotOptions,
                xAxis: {
                    maxZoom: 1 * 24 * 3600000, // fourteen days
                    ordinal: false
                },
                yAxis: {
                    min: 0,
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
                series: jQuery.parseJSON(data)
            });
			series = jQuery.parseJSON(data);
			allSeries.push(series);
			if(allSeries.length==5){
				multiGraph();
			}
        } else {
            var div = document.getElementById(graphParams.divid);
            div.innerHTML="<div id='error'><b>Insufficient Data</b></div>";
        }
		$('#load_bar').hide();
    }
}

function onSuccessCompare(graphParams,country) {
    return function(data) {
        if (data.length > 200) {
            window.chart = new Highcharts.StockChart({
                chart: {
                    renderTo: graphParams.divid,
                },
                legend: graphParams.legend,
                rangeSelector: graphParams.rangeSelector,
                plotOptions: graphParams.plotOptions,
                xAxis: {
                    maxZoom: 1 * 24 * 3600000, // fourteen days
                    ordinal: false
                },
                yAxis: {
                    min: 0,
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
                series: JSON.parse(data)[1]
            });
        } else {
            var div = document.getElementById(graphParams.divid);
            div.innerHTML="<div id='error'><b>Insufficient Data</b></div>";
        }
		if (data.length > 200) {
			data = JSON.parse(data)[0];
			var graphData = new Array();
			var categories = new Array();
			for(var i=0;i<data.length; i++){
				graphData[i] = {
					y : parseFloat(data[i]['data']),
					name : data[i]['name'],
					country : country
				}
				if (data[i]['count']=='1'){
					categories[i] = data[i]['name'] + ' (' + data[i]['count'] + ')';
				}
				else{
					categories[i] = data[i]['name'] + ' (' + data[i]['count'] + ')';
				}
			}
            window.chart2 = new Highcharts.Chart({
                chart: {
					type: 'column',
                    renderTo: graphParams.divid2,
                },
				title: {
					text: 'Performance Averages'
				},
				yAxis:{
					title:{
						text: graphParams.units
					}
				},
				xAxis:{
					categories: categories,
					labels:{
						rotation: 90,
						justify: false,
						y: 55,
						style: {
							fontWeight: 'bold'
						}
					}
				},
				plotOptions: graphParams.plotOptions,
				tooltip:{
					formatter: function(){
						var units;
						var val;
						if (graphParams.units == "Bits Per Second"){
							units = "Mbps";
							val = recDivide(this.y, this.y, 0);
						}
						else{
							units = "ms";
							val = this.y;
						}
						return val.toFixed(2) + units;
					}
				},
				legend:{
					enabled: false
				},
				series: [{
					data: graphData,
					name: categories
				}]
            });
        } else {
            var div = document.getElementById(graphParams.divid2);
            div.innerHTML="<div id='error'><b>Insufficient Data</b></div>";
        }
		$('#load_bar').hide();
    }
}

function onSuccessCountryCompare(graphParams, country) {
    return function(data) {
		if (data.length > 200) {
			data = JSON.parse(data)[0];
			var graphData = new Array();
			var categories = new Array();
			for(var i=0;i<data.length; i++){
				graphData[i] = {
					y : parseFloat(data[i]['data']),
					name : data[i]['name'],
					country : country				
				}
				if (data[i]['count']=='1'){
					categories[i] = data[i]['name'] + ' (' + data[i]['count'] + ')';
				}
				else{
					categories[i] = data[i]['name'] + ' (' + data[i]['count'] + ')';
				}
			}
            window.chart2 = new Highcharts.Chart({
                chart: {
					type: 'column',
                    renderTo: graphParams.divid,
                },
				title: {
					text: 'Performance Averages'
				},
				yAxis:{
					title:{
						text: graphParams.units
					}
				},
				xAxis:{
					categories: categories,
					labels: {
						rotation: 90
					}
				},
				plotOptions: graphParams.plotOptions,
				tooltip:{
					formatter: function(){
						var units;
						var val;
						if (graphParams.units == "Bits Per Second"){
							units = getUnits(this.y);
							val = recDivide(this.y, this.y, 0);
						}
						else{
							units = "ms";
							val = this.y;
						}
						return val.toFixed(2) + units;
					}
				},
				legend:{
					enabled: false
				},
				series: [{
					data: graphData,
					name: categories
				}]
            });
        } else {
            var div = document.getElementById(graphParams.divid2);
            div.innerHTML="<div id='error'><b>Insufficient Data</b></div>";
        }
		$('#load_bar').hide();
    }
}

function compareGraphs(deviceid){
	$('#load_bar').show();
	var sel1 = document.getElementById("max_devices");
	var sel2 = document.getElementById("compare_criteria");
	var sel3 = document.getElementById("measurement_type");
	var sel4 = document.getElementById("days");
	var max = sel1.options[sel1.selectedIndex].value;
	var cri = sel2.options[sel2.selectedIndex].value;
	var mtype = sel3.options[sel3.selectedIndex].value;
	var serverloc = sel3.options[sel3.selectedIndex].text;
	var days = sel4.options[sel4.selectedIndex].value;
	var params = compareParameters(mtype);
	$.ajax({
		type: "GET",
		url: params.url,
		data: {'days': days,'server_loc': serverloc, 'direction' : params.direction, 'graphno' : params.graphno, 'device': deviceid, 'filter_by': filter, 'max_results': max, 'criteria': cri},
		success: onSuccessCompare(params)
	});
}

function compareByCity(city, country){
	$('#load_bar').show();
	var sel1 = document.getElementById("max_devices");
	var sel2 = document.getElementById("measurement_type");
	var sel3 = document.getElementById("days");
	var max = sel1.options[sel1.selectedIndex].value;
	var mtype = sel2.options[sel2.selectedIndex].value;
	var days = sel3.options[sel3.selectedIndex].value;
	var params = compareByCityParameters(mtype);
	$.ajax({
		type: "GET",
		url: params.url,
		data: {'days': days, 'direction' : params.direction, 'graphno' : params.graphno,'max_results': max, 'city' : city},
		success: onSuccessCompare(params,country)
	});
}

function compareByCountry(country){
	$('#load_bar').show();
	var sel1 = document.getElementById("max_devices");
	var sel2 = document.getElementById("measurement_type");
	var sel3 = document.getElementById("days");
	var max = sel1.options[sel1.selectedIndex].value;
	var mtype = sel2.options[sel2.selectedIndex].value;
	var days = sel3.options[sel3.selectedIndex].value;
	var params = compareByCountryParameters(mtype);
	$.ajax({
		type: "GET",
		url: params.url,
		data: {'days': days, 'direction' : params.direction, 'graphno' : params.graphno,'max_results': max, 'country' : country},
		success: onSuccessCountryCompare(params, country)
	});
}

function compareByIsp(isp,country){
	$('#load_bar').show();
	var sel1 = document.getElementById("max_devices");
	var sel2 = document.getElementById("measurement_type");
	var sel3 = document.getElementById("days");
	var max = sel1.options[sel1.selectedIndex].value;
	var mtype = sel2.options[sel2.selectedIndex].value;
	var days = sel3.options[sel3.selectedIndex].value;
	var params = compareByIspParameters(mtype, country, isp);
	$.ajax({
		type: "GET",
		url: params.url,
		data: {'days': days, 'direction' : params.direction, 'graphno' : params.graphno,'max_results': max, 'isp' : isp, 'country' : country},
		success: onSuccessCompare(params)
	});
}

function renderGraphs(deviceid) {
    for (var i = 0; i < 6; ++i) {
        var params = createParameters(i);
        $.ajax({
            type: "GET",
            url: params.url,
            data: {'graphno' : params.graphno, 'deviceid': deviceid, 'filter_by': filter},
            success: onSuccessGraph(params)
        });
    }
}

function multiGraph(){
	var downloadString = "Download Throughput";
	var uploadString = "Upload Throughput";
	var RTTString = "RTT (Georgia Tech)";
	var LMString = "Last Mile Latency";
	var shaperateString = "Shape Rate (down)"
	var multiSeries = new Array();
	var i,j;
	for(i=0; i<allSeries.length; i++){
		for (j=0; j<allSeries[i].length; j++){
			if (allSeries[i][j].priority==1){
				switch(allSeries[i][j].id){
					case 1:
						allSeries[i][j].name = downloadString;
						allSeries[i][j].yAxis = 0;
						break;
					case 2:
						allSeries[i][j].name = uploadString;
						allSeries[i][j].yAxis = 0;
						break;
					case 3:
						allSeries[i][j].name = RTTString;
						allSeries[i][j].yAxis = 1;
						break;
					case 4:
						allSeries[i][j].name = LMString;
						allSeries[i][j].yAxis = 1;
						break;
					case 5:
						allSeries[i][j].name = shaperateString;
						allSeries[i][j].yAxis = 0;
						break;
				}
				multiSeries.push(allSeries[i][j]);
			}
		}
	}
	window.chart = new Highcharts.StockChart({
		chart: {
			renderTo: "graph_div_7"
		},
		legend: {
            enabled: true,
            align: 'center',
            verticalAlign: 'top',
            borderColor: '#ddd',
            borderWidth: 1,
            shadow: false
        },
		rangeSelector: {
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
        },
		xAxis: {
			maxZoom: 1 * 24 * 3600000, // fourteen days
			ordinal: false
		},
		yAxis: [{
			min: 0,
			title: {
				text: "Bits Per Second",
				style:{
					fontSize: 15
				}
			}
		},{
			min: 0,
			title: {
				text: "Milliseconds",
				style:{
					fontSize: 15
				}
			},
			opposite:true
		}],
		plotOptions: {
            line: {
                gapSize: 10
            }
        },
		tooltip: {
			shared: false,
            formatter: function() {
				var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                // $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    // ret += '<p style="color:' + point.series.color +  ';">';
                    // ret += point.series.name + '</p> ';
					// switch(point.series.name){
						// case uploadString:
							// ret += formatBytes(point.y) + '<br/>';
							// break;
						// case downloadString:
							// ret += formatBytes(point.y) + '<br/>';
							// break;
						// case RTTString:
							// ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
							// break;
						// case LMString:
							// ret += '<b>'+ parseInt(point.y) +'</b> milliseconds<br/>';
							// break;
					// }
                // });
				ret += '<p style="color:' + this.series.color +  ';">';
                ret += this.series.name + '</p> ';
				switch(this.series.name){
					case uploadString:
						ret += formatBytes(this.y) + '<br/>';
						break;
					case downloadString:
						ret += formatBytes(this.y) + '<br/>';
						break;
					case RTTString:
						ret += '<b>'+ parseInt(this.y) +'</b> milliseconds<br/>';
						break;
					case LMString:
						ret += '<b>'+ parseInt(this.y) +'</b> milliseconds<br/>';
						break;
					case shaperateString:
						ret += formatBytes(this.y) + '<br/>';
						break;					
				}
                return ret;
            }
        },
		series: multiSeries
	});
}
