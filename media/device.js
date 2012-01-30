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

}

function hideBar(id){
    document.getElementById("load_bar_" + id).style.display='none'
}

function OnError(data)
{
  alert("data loading failed");
}
