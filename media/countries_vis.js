var servers = []

function fillmap(index) {
    $('#world-map').off().empty();
    $.ajax({
		type : 'GET',
		url : 'get_countries_vis_data/',
		data : { 'startdate' : $('#startdate').val(),
			 'enddate' : $('#enddate').val(),
			 'serverip' : servers[index].ip
		},
		success : function(result) {
				drawRegionsMap(result, index);
		}
    });
}

function drawRegionsMap(response, server_index) {
    response = JSON.parse(response);
    var mapdata = {};
    var condetail = {};
    $.each(response, function(key, value) {
	if (value[2] > 500) {    //measurements threshold
	    mapdata[value[0]] = value[3];
	    condetail[value[0]] = { ndevices : value[1], nmeasurements : value[2], latency : value[3] };
	}
    });

    $('#world-map').off().empty();
    var map = new jvm.WorldMap({
	container : $('#world-map'),
        map : 'world_mill_en',
	markersSelectable : true,
        series : {
            regions : [ {
                values : mapdata,
		scale : ['#FEE5D9', '#A50F15'],
		min : 0,
		max : 500
            } ]
        },

	regionStyle : {
	    initial : {
		fill : '#FFFF99'
	    }
	},
	backgroundColor : '#006694',

        markerStyle : {
            initial : {
                fill : '#000000',
                stroke : '#ffffff'
            },
	    selected : {
		fill : '#4DAC26',
		r : 7
	    }
        },

        markers : servers,

	onRegionClick : function(e, code) {
	    var name = map.getRegionName(code);

	    if(name === 'United States of America')
		name = 'United States';

	    window.location = 'http://dev.networkdashboard.org/compare_by_country/' + name;
	},

	onMarkerClick : function(e, code) {
	    if(code == server_index)
		return;
	    map.label.hide();
	    fillmap(code);
	},

	onMarkerLabelShow : function(e, el, code) {
	    if(code != server_index)
		el.html( el.html() + " - Click to select" );
	},

	onMarkerSelected : function(e, code, isSelected, selectedMarkers) {
	    if(code != server_index)
		return;
	    map.setSelectedMarkers([code]);
	},

        onRegionLabelShow : function(e, el, code) {
            countryName = el.html().replace(/<(?:.|\n)*?>/gm, '');
	    
	    if (condetail[code] != null)
		el.html("<b>" + countryName + "</b><br/><br/>Average Latency: " + Math.round(condetail[code]['latency']) + " ms<br/>" + condetail[code]['ndevices'] + " device(s)<br/>" + condetail[code]['nmeasurements'] + " Measurements<br/><br/>Click for details");

	    else
		el.html("<b>" + countryName + "</b><br/><br/>Not enough measurements for devices in this country, in this date range");
        }
    });

    map.setSelectedMarkers([server_index]);
    $('#serverselector').val(server_index);
};

$(document).ready(function() {
    $('#enddate').val(moment().endOf('day').format('YYYY-MM-DD'));
    $('#calendar').daterangepicker(
	{
	    format : 'YYYY-MM-DD',
	    startDate : $('#startdate').val(),
	    endDate : $('#enddate').val(),
		separator : ' to '
	},
	function(start, end){
	    $('#startdate').val(start.format('YYYY-MM-DD'));
	    $('#enddate').val(end.format('YYYY-MM-DD'));
	    fillmap($('#serverselector').val());
	}
    );
    $('#serverselector').change(function() {
	fillmap($('#serverselector').val());
    });
    $('#serverselector').val(9);
    fillmap(9);
});
