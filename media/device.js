hashid="";
tabid=1;

function setHashid(data){
	hashid=data;
}

function expandUploadDesc() {
    $('#upload_desc_content').show();
    $('#upload_desc').hide();
    return false;
}

function collapseUploadDesc() {
    $('#upload_desc_content').hide();
    $('#upload_desc').show();
    return false;
}
function expandRttDesc() {
    $('#rtt_desc_content').show();
    $('#rtt_desc').hide();
    return false;
}

function collapseRttDesc() {
    $('#rtt_desc_content').hide();
    $('#rtt_desc').show();
    return false;
}

function expandLmrttDesc() {
    $('#lmrtt_desc_content').show();
    $('#lmrtt_desc').hide();
    return false;
}

function collapseLmrttDesc() {
    $('#lmrtt_desc_content').hide();
    $('#lmrtt_desc').show();
    return false;
}

function expandDownloadDesc() {
    $('#download_desc_content').show();
    $('#download_desc').hide();
    return false;
}

function collapseDownloadDesc() {
    $('#download_desc_content').hide();
    $('#download_desc').show();
    return false;
}

function collapseDesc() {
	collapseUploadDesc();
	collapseDownloadDesc();
	collapseRttDesc();
	collapseLmrttDesc();
}

function setTabid(data){
	tabid=data;
}

function getHashid(data){
	hashid=data;
}

function getTabid(data){
	tabid=data;
}

function feedback(link,windowname){
    if (!window.focus){
        return true;
    }
    var href;
    if (typeof(mylink) == 'string'){
       href=link;
    }
    else{
       href=link.href;
    }
    window.open(href, windowname, 'width=500,height=200,scrollbars=yes,location=0,status=0');
    return false;
}

function changeTab(active, total, tab, content) {  

    for (var i=1; i < total+1; i++) {  
      document.getElementById(content+i).style.display = 'none';  
      document.getElementById(tab+i).className = '';  
    }  
    document.getElementById(content+active).style.display = 'block';  
    document.getElementById(tab+active).className = 'selected';
    setTabid(active);
	updateShareLink();
}

function updateShareLink(){
	document.getElementById('url').value =  window.location.hostname + "/display_device/" + hashid + "?tab=" + tabid;
}

function hideBar(id){
    /*document.getElementById("load_bar_" + id).style.display='none'*/
}

function OnError(data)
{
  alert("data loading failed");
}

function getParameterByName(name)
{
  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
  var regexS = "[\\?&]" + name + "=([^&#]*)";
  var regex = new RegExp(regexS);
  var results = regex.exec(window.location.search);
  if(results == null)
    return '';
  else
    return decodeURIComponent(results[1].replace(/\+/g, " "));
}
