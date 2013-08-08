function fillmap() {
    ip = $("#serverselector").val();
    name = $("#serverselector option:selected").text();
    $('#world-map').off().empty();
    $.ajax({
        url : ("get_countries_vis_data/" + ip),
        success : function(result) {
            drawRegionsMap(result, name);
        }
    });
}

function drawRegionsMap(response, server_name) {
    response = JSON.parse(response);

    color_pallette = ['#003399', '#009900', '#FFCC00', '#CC0000', '#000000'];

    colors = {};
    $.each(response['mapdata'], function(key, value) {
	index = Math.floor(value[0]/100);
	if(index > 4)
	    index = 4;

        colors[key] = color_pallette[index];
    });

    $('#updatedon > i').text("Last updated on: " + response['eventstamp']);

    $('#world-map').off().empty();

    $('#world-map').vectorMap({
        map : 'world_mill_en',
        series : {
            regions : [ {
                values : colors,
                attribute : 'fill'
            } ]
        },
        markerStyle : {
            initial : {
                fill : '#000000',
                stroke : '#ffffff'
            }
        },

        markers : [ {
            latLng : [ response['server']['lat'], response['server']['lon'] ],
            name : server_name + " server"
        } ],

	onRegionClick : function(e, code) {
	    var map = $('#world-map').vectorMap('get', 'mapObject');
	    var name = map.getRegionName(code);

	    if(name === 'United States of America')
		name = 'United States';

	    window.location = 'http://dev.networkdashboard.org/compare_by_country/' + name;
	},
        onRegionLabelShow : function(e, el, code) {
            countryName = el.html().replace(/<(?:.|\n)*?>/gm, '');
	    
	    if (response['mapdata'][code] != null)
		el.html("<b>" + countryName + "</b><br/><br/>Average latency: " + Math.round(response['mapdata'][code][0]) + " ms<br/>Measured from " + response['mapdata'][code][1] + " device(s)<br/><br/>Click for details");

	    else
		el.html("<b>" + countryName + "</b><br/><br/>Sorry, we do not have enough devices in this country");
        }
    });

};

$(document).ready(function() {
    fillmap();
    $('#serverselector').change(fillmap);
});
