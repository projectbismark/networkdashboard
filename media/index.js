var points = new Array();
var markers = new Array();
/*
//delay after panning to new location
var delay = 5000;
//delay between zoomout-pan-zoomin
var animationDelay = 700;
//delay between zoom levels (currently bugs with googles continuous zoom methods, so this must be handled manually)
var innerAnimationDelay = 30;
*/

//threshold for panning map. Map will pam to the closest, unvisited node that is at least this far away (in kilometers)
var thresh = 1000;
var minZoom = 1;
var maxZoom = 5;
var currentMarker;
var infowindow = new InfoBubble({
    	arrowSize: 7,
    	disableAutoPan: false,
    	hideCloseButton: true,
});
var boxText = document.createElement("p");
boxText.style.cssText = "font-size:12px; margin-bottom:-3px";

function MapPoint(latLng) {
    this.visited = false;
    this.latLng = latLng;
}
/*

function resetPoints() {
    for (var i = 0;i < points.length; ++i) {
        points[i].visited = false;
    }
}

function zoomIn() {
    var z = map.getZoom();
    if (z < maxZoom) {
        map.setZoom(z + 1);
        setTimeout(function(){zoomIn()}, innerAnimationDelay);
    }
}

function zoomOut() {
    var z = map.getZoom();
    if (z > minZoom) {
        map.setZoom(z - 1);
        setTimeout(function(){zoomOut()}, innerAnimationDelay);
    }
}

function panMap(coords) {
    map.panTo(coords);
}
*/

function load() {
    var mid = new google.maps.LatLng(0, 0);
    var options = {
        zoom: 1,
        center: mid,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false
    };

    map = new google.maps.Map(document.getElementById("map"),options);
    geocoder = new google.maps.Geocoder();

    $.ajax({
        type: "GET",
        url: "/getCoordinates/",
        success: OnSuccess
    });
    /*
    setTimeout(function(){cycleMap()}, delay);
    */

    var hosts = ['myrouter.projectbismark.net', 'myrouter.local', '192.168.142.1'];
    for (var idx in hosts) {
        $.ajax({
            type: "GET",
            url: "http://" + hosts[idx] + "/cgi-bin/dashboard-verify",
            success: function(data, textStatus, jqXHR) {
                var node_id = $.trim(data);
                if (node_id.length == 12) {
                    $("#node_id").val(node_id);
                    $("#view_button").removeAttr("onclick");
                }
            }
        });
    }
    
    google.maps.event.addListener(map, "click", function() { 
		if (infowindow) { 
			infowindow.close(); 
		} 
	}); 
}

function expandEntry() {
    $('#view_button').addClass('disabled');
    $('#view_button').removeClass('btn-primary');
    return expandAdvanced();
}

function expandAdvanced() {
    $('#detection_error').show();
    $('#error_mac').focus();
    $('#advanced').hide();
    return false;
}


/*
function cycleMap(){
    var mid = map.getBounds().getCenter();
    var next = mid;
    //in kilometers
    var shortestDist = 0;
    for(var i = 0; i < points.length; ++i) {
        if (!points[i].visited) {
            var d = google.maps.geometry.spherical.computeDistanceBetween(mid,points[i].latLng)/1000;
            if (d < thresh) {
                points[i].visited=true;
            }
            else if (d < shortestDist || shortestDist == 0) {
                next = points[i];
                shortestDist = d;
            }
        }
    }
    if (shortestDist==0){
        resetPoints();
        cycleMap();    
    }
    else{
        zoomOut();
        setTimeout(function() { panMap(next.latLng) }, animationDelay);
        setTimeout(function() { zoomIn() }, animationDelay * 2);
        setTimeout(function() { cycleMap() }, delay + animationDelay * 2);
    }
}
*/

/*
function createMarker(c) {
	var point = new google.maps.LatLng(parseFloat(c[2]), parseFloat(c[3]));
    points.push(new MapPoint(point));
	var marker = new google.maps.Marker({
		position: point
    });
    marker.devicehash = c[4];
	google.maps.event.addListener(marker, "click", function() {
		boxText.innerHTML = "<a href=\"http://networkdashboard.org/displayDevice/" + marker.devicehash + "\">Show Router Details</a>";
		infowindow.setContent(boxText);
		infowindow.open(map, marker);
	});
	if (c[0] == "server") {
		marker.setIcon("/static/images/icon-blue.png");
	} else {
		marker.setIcon("/static/images/icon-red-dot.png");
	}
	marker.setMap(map);
}*/

function createMarker(d) {
	var point = new google.maps.LatLng(parseFloat(d.lat), parseFloat(d.lon));
    points.push(new MapPoint(point));
	var marker = new google.maps.Marker({
		position: point
    });
    marker.devicehash = d.hash;
	marker.isp = d.isp;
	marker.server = int(d.server);
	marker.active = int(d.active);
	if (marker.devicehash != ""){
		google.maps.event.addListener(marker, "click", function() {
			boxText.innerHTML = "<a href=/displayDevice/" + marker.devicehash + "\">Show Router Details</a>";
			infowindow.setContent(boxText);
			infowindow.open(map, marker);
		});
	}
	if (d.server == 1) {
		marker.setIcon("/static/images/icon-blue.png");
	}
	else if (d.active ==1) {
		marker.setIcon("/static/images/icon-green-dot.png");
	}
	else {
		marker.setIcon("/static/images/icon-red-dot.png");
	}
	marker.setMap(map);
	markers.push(marker);
}
	
	/*
	google.maps.event.addListener(marker, "click", function() {
		if(marker.called == false) {
			$.ajax({
				type: "GET",
				url: "/getLatestInfo/",
				data: {'devicehash': marker.devicehash},
				success: function(data){OnSuccessMarker(data, marker);}
			});
			marker.called = true;
		}
		
		if(marker.content == "Loading...")
			boxText.innerHTML = marker.content;
		else if(marker.content != "NOT AVAILABLE")
			boxText.innerHTML = marker.content + 
				"<a href=\"http://networkdashboard.org/displayDevice/" + marker.devicehash + 
				"\">Show Router Details</a>";
		else
			boxText.innerHTML = "Information not available.";
		
		infowindow.setContent(boxText);
		infowindow.open(map, marker);
	});*/

function OnSuccessMarker(data, marker) {
	marker.content = data;
	if(marker.content != "NOT AVAILABLE")
		boxText.innerHTML = marker.content + 
			"<a href=\"http://networkdashboard.org/displayDevice/" + marker.devicehash + 
			"\">Show Router Details</a>";
	else
		boxText.innerHTML = "Information not available.";
	infowindow.setContent(boxText);
	infowindow.close();
	infowindow.open(map, marker);
}

function FilterProviders(sel) {
	var val = sel.options[sel.selectedIndex].value;
	var hideUnregistered = document.getElementById("filter_unregistered").checked;
	if (val=="none"){
		for (var i=0; i<markers.length; i++){
			if((markers[i].dev_type!="unregistered")||(hideUnregistered = false)){	
				markers[i].setVisible(true);
			}
		}
	}
	else{
		for (var i=0; i<markers.length; i++){
			if (markers[i].isp != val){
				markers[i].setVisible(false);
			}
			else{
				if ((markers[i].dev_type!="unregistered")||(hideUnregistered == false)){
					markers[i].setVisible(true);
				}
			}
		}
	}
}

function HideUnregistered(hide) {
	var sel = document.getElementById("filter_isp")
	var isp = sel.options[sel.selectedIndex].value;
	for (var i=0; i<markers.length; i++){
		if (markers[i].dev_type == "unregistered"){
			if(hide==true){
				markers[i].setVisible(false);
			}
			else{
				if((isp=="none")||(markers[i].isp==isp)){
					markers[i].setVisible(true);
				}
			}
		}
	}
}

/*function OnSuccess(data) {
    var coordstring = data.split("\n");
    for (var i = 0; i < coordstring.length - 1; ++i){
        var coords = coordstring[i].split(":");
        if (coords[1] == 'coord') {
            createMarker(coords);
        } else {
            geocoder.geocode({ 'address': coords[2]}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    var marker = new google.maps.Marker({
                        map: map,
                        position: results[0].geometry.location
                    });
                }
            });
        }
    }
}*/

function OnSuccess(data) {
	var dict = eval(data);
	for (d in dict){
		createMarker(dict[d]);
	}
}

function GUnload(){
    if (window.GUnloadApi) {
        GUnloadApi();
    }
}