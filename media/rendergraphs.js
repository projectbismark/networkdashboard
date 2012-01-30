var filter = "none"; 

function createParameters(i){
    var graphid = 1;
    var url = "/line_bitrate/";
    var graphno = 1;
    var divid = "graph_div_1";
    var titlename ="Download Throughput";
    var formatter = function(){};
    var legend = {
        enabled: true,
        align: 'right',
        backgroundColor: '#FCFFC5',
        borderColor: 'black',
        borderWidth: 2,
        layout: 'vertical',
        verticalAlign: 'top',
        y: 100,
        shadow: true
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
                type: 'ytd',
                text: 'YTD'
        }, {
                type: 'year',
                count: 1,
                text: '1y'
        }, {
                type: 'all',
                text: 'All'
        }],
        selected: 1
    };
    var plotoptions = {};
    var units = "KBps";


    switch (i){
        case 0:
            formatter = function(){
                    return ''+ '<p style="color:' + this.points[0].series.color +  ';">' + this.points[0].series.name+ '</p><br />'+ Highcharts.dateFormat('%A,%e. %b %Y, %l %p', this.x) +' <br/><b>'+ parseInt(this.points[0].y)+'</b> KBps';
                };
            graphid = 0;
            break;
            
        case 1:
            divid = "graph_div_2";
            graphno = 2;
            titlename = "Upload Throughput";
            graphid = 1;
            break;
        case 2:
            units = "msec";
            titlename = "Round-Trip Time";
            divid = "graph_div_3";
            url = "/line_rtt/";
            formatter = function(){
                return ''+ '<p style="color:' + this.points[0].series.color +  ';">' + this.points[0].series.name+ '</p><br />' + Highcharts.dateFormat('%A, %e. %b %Y, %l:%M %p', this.x) +' <br/><b>'+ parseInt(this.points[0].y) +'</b> msec';
            }
            graphid = 2;
            break;
        case 3:
            units = "msec";
            titlename = "Last Mile Latency";
            divid = "graph_div_4";
            url = "/line_lmrtt/";
            formatter = function(){
                return ''+ '<p style="color:' + this.points[0].series.color +  ';">' + this.points[0].series.name+ '</p><br />'+ Highcharts.dateFormat('%A, %e. %b %Y, %l:%M %p', this.x) +' <br/><b>'+ parseInt(this.points[0].y) +'</b> msec';
            }
            graphid = 3;
            break;

        case 4:
            titlename = "Passive Data";
            divid = "graph_div_5";
            units = "MB";
            url = "/line_passive/";
            formatter = function(){
                return ''+ '<p style="color:' + this.points[0].series.color +  ';">' + this.points[0].series.name+ '</p><br />'+ Highcharts.dateFormat('%A,%e. %b %Y, %l %p', this.x) +' <br/><b>'+ parseInt(this.points[0].y/1000/1000) +'</b> MB';
            };
            plotoptions ={
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
            backgroundColor: "rgb(249,249,255)"
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
