var markers = new Array();
var infowindow = new InfoBubble({
    	arrowSize: 7,
    	disableAutoPan: false,
    	hideCloseButton: true,
});
var boxText = document.createElement("p");
boxText.style.cssText = "font-size:12px; margin-bottom:-3px";

function load() {
    var mid = new google.maps.LatLng(0, 0);
    var options = {
        zoom: 1,
        center: mid,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false
    };
    map = new google.maps.Map(document.getElementById("map"),options);
    $.ajax({
        type: "GET",
        url: "/get_coordinates/",
        success: onSuccess
    });
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

function createMarker(d) {
	var point = new google.maps.LatLng(parseFloat(d.lat), parseFloat(d.lon));
	var marker = new google.maps.Marker({
		position: point
    });
    marker.devicehash = d.hash;
	marker.isp = d.isp;
	marker.server = parseInt(d.server);
	marker.active = parseInt(d.active);
	if (marker.devicehash != ""){
		google.maps.event.addListener(marker, "click", function() {
			boxText.innerHTML = "<a href=/display_device/" + marker.devicehash + "\">Show Router Details</a>";
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

function filterProviders(sel) {
	var val = sel.options[sel.selectedIndex].value;
	var hidden = document.getElementById("filter_unregistered").checked;
	if (val=="none"){
		for (var i=0; i<markers.length; i++){
			if((markers[i].dev_type!="unregistered")||(hidden = false)){	
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
				if ((markers[i].dev_type!="unregistered")||(hidden == false)){
					markers[i].setVisible(true);
				}
			}
		}
	}
}

function hideUnregistered(hide) {
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

function onSuccess(data) {
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