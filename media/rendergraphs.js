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
                gapSize: null
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
            ret.units = 'Bytes Per Second';
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
            ret.units = "Bytes Per Second";
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
            ret.graphid = 3;
            ret.formatter = function() {
                var ret = Highcharts.dateFormat(dateFormatString, this.x) + "<br/>";
                $.each(this.points.sort(sortOrdinatesDescending), function(idx, point) {
                    ret += '<p style="color:' + point.series.color +  ';">';
                    ret += point.series.name + '</p> ';
                    ret += formatBytes(point.y) + '<br/>';
                });
                return ret;
            };
            ret.units = 'Bytes Per Second';
            ret.url = "/line_shaperate/";
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
                series: JSON.parse(data)
            });
        } else {
            var div = document.getElementById(graphParams.divid);
            div.innerHTML="<div id='error'><b>Insufficient Data</b></div>";
        }
    }
}

function renderGraphs(deviceid) {
    for (var i = 0; i < 5; ++i) {
        var params = createParameters(i);
        $.ajax({
            type: "GET",
            url: params.url,
            data: {'graphno' : params.graphno, 'deviceid': deviceid, 'filter_by': filter},
            success: onSuccessGraph(params)
        });
    }
}
