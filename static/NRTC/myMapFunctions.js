
var map;
var markerArray = [];
itemTypes = ["toilet", "food", "school","parking","standout","warning","hospital","military"];

for (i=0;i<itemTypes.length;i++){
    var action = itemTypes[i];
    if (action!="hospital" && action != "military"){
        (function(action){
        var myNode= document.querySelector('#'+action);

        console.log("mynode",myNode);
        console.log(action);
        myNode.addEventListener("click",function(e){
         toggle_function(String(action));
        });

        })(action);
    }

}

var myNode= document.querySelector('#line');
myNode.addEventListener("click",function(e){
 toggle_function("line");
});

var line;
var CPMarker;


function openModal(evt) {
    // Get the modal
    var modal = document.getElementById('myModal');
    console.log(modal);
    console.log("ahahahah ");
    // Get the button that opens the modal

    var span = document.getElementsByClassName("close")[0];


    modal.style.display = "block";


    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}




function initMap(data) {
   console.log("after get map call",data);
   for (i=0;i<markerArray.length;i++){
        marker = markerArray[i];
        marker["marker"].setMap(null);
   }
   markerArray = [];
   var centre=data["centre"];
   items = data["items"];
   lineData = data["lineData"];
   if (centre.length > 0){
      map = new google.maps.Map(document.getElementById('map'), {
        zoom: 17,
        draggableCursor:'default',
        center: {lat: centre[0], lng: centre[1]}  // Center the map on Chicago, USA.
      });
      }
  CPMarker = new google.maps.Marker({position:{lat:centre[0],lng:centre[1]},

                                            draggable:false,
                                            map:map
                                            });

        outerdiv = document.createElement("div");
        span = document.createElement("span");
        span.innerText = "Line Info";
        outerdiv.appendChild(span);
        div = document.createElement("div");
        info = document.createElement("textarea");
        if(lineData["info"]){
            info.value = lineData["info"];
        }
        else{
            info.value = "";
        }
        info.cols = 30;
        info.rows = 4;
        div.appendChild(info);
        outerdiv.appendChild(div);
   console.log("------------------------------------------------");
   var infoWindow = new google.maps.InfoWindow({
                    content:outerdiv,
                });
            CPMarker.addListener('click', function() {
                    infoWindow.open(map, CPMarker);
                  });
  CPMarker.infoWindow = infoWindow;
  google.maps.event.addListener(map,'click', function(event) {
    map_clicked(event);
  });
  for (var i = 0; i < items.length; i++) {
        console.log(items[i]);
        var icon = {
                url:"/static/NRTC/" + items[i]["itemType"] + ".png",
                scaledSize:new google.maps.Size(40,40)
                }
       markerDict = create_marker(icon,items[i]["info"],items[i]["permissions"],items[i]["lat"],items[i]["lon"],items[i]["itemType"],items[i]["first"],items[i]["accessMethod"]);
       markerDict["first"] = items[i]["first"]
       markerDict["id"] = items[i]["id"];
       markerDict["itemType"] = items[i]["itemType"]
       markerArray.push(markerDict);
       google.maps.event.trigger(map, "resize");

}
console.log("line data length is",lineData.length);
if (lineData["coords"]){
        line = new google.maps.Polyline({
                editable: true,
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2,
                map: map
              });

        var lineInfoWindow = new google.maps.InfoWindow({
                    content:outerdiv,
                    line:line,
                });
            line.addListener('click', function() {
                    lineInfoWindow.open(map, CPMarker);
                  });
        for(i=0;i<lineData["coords"].length;i++){
            line.getPath().push(new google.maps.LatLng(lineData["coords"][i]));

        }
        line.lineInfoWindow = lineInfoWindow;
   }



}

get_map();


var currentFunction;



var toiletArray = [];

var foodArray = [];

var schoolArray = [];

var infoArray = [];

var toiletMarker;
var foodMarker;
var schoolMarker;






function add_marker(event,icon){
    var marker = new google.maps.Marker({position:event.latLng,
                                        icon:icon,
                                        draggable:true,
                                        map:map
                                        });

    return marker;

}


function delete_marker(marker,itemType){
    var num = 0;
    for (var i = 0;i<markerArray.length;i++){
        if (markerArray[i]["itemType"] == itemType && markerArray[i]["marker"].map){
            num+=1;
        }

    }
    for (var i=0;i<markerArray.length;i++){
        if (markerArray[i]["marker"] == marker){
            if(markerArray[i]["first"]){
                if (num > 1){
                    alert("You cannot delete the primary marker if there is more than one marker of the same type");
                    return;
                }
            }
        }
    }
    marker.setMap(null);
}


function toggle_function(action){
    el = document.getElementById(action);
    if (currentFunction === undefined){
        currentFunction = action;
        document.body.style.cursor = 'crosshair';
        map.set("draggableCursor",'crosshair');
        el.style["boxShadow"] = null;
        el.style["boxShadow"] = "0px 0px 35px rgba(255, 0, 255, 0.9)";
    }
    else{
        if (currentFunction === "line" & line !== undefined) {
            var path = line.getPath();
            var lineLength = path.getLength();
            if (action !== "line" & lineLength < 2){
                 line.setMap(null);
                 line = undefined;
                 el = document.getElementById("line");
                 el.style.boxShadow = null;
                 currentFunction = action;
            }
            if (action === "line" & lineLength ===2){
                el = document.getElementById("line");
                 el.style.boxShadow = null;
                 currentFunction = undefined;
                 document.body.style.cursor = 'default';
                map.set("draggableCursor",'default');
            }
        }
        else{
            var el = document.getElementById(currentFunction);
            console.log(el);
            console.log(el.style.boxShadow);
            el.style.boxShadow = null;

            if (action !== currentFunction){
                el = document.getElementById(action);
                el.style["boxShadow"] = null;
                el.style["boxShadow"] = "0px 0px 35px rgba(255, 0, 255, 0.9)";
                currentFunction = action;
                document.body.style.cursor = 'crosshair';
                map.set("draggableCursor",'crosshair');
            }
            else{
                currentFunction = undefined;
                document.body.style.cursor = 'default';
                map.set("draggableCursor",'default');}
            }
    }
}

function map_clicked(event){
    console.log("clicked,current function is " + currentFunction)
    console.log(event);
    if (currentFunction === undefined){

    }
    else{
        if (currentFunction === "line"){
            if (line === undefined){
                line = new google.maps.Polyline({
                editable: true,
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2,
                map: map
              });
            outerdiv = document.createElement("div");
        span = document.createElement("span");
        span.innerText = "Line Info";
        outerdiv.appendChild(span);
        div = document.createElement("div");
        info = document.createElement("textarea");
        info.value = "";
        info.cols = 30;
        info.rows = 4;
        div.appendChild(info);
        outerdiv.appendChild(div);
        var lineInfoWindow = new google.maps.InfoWindow({
                    content:outerdiv,
                    line:line,
                });
            line.addListener('click', function() {
                    lineInfoWindow.open(map, CPMarker);
                  });
        line.lineInfoWindow = lineInfoWindow;
            }

            console.log("in map, value of currentFunction is " + currentFunction);
            var path = line.getPath();
            console.log("wer");
          if(path.getLength() > 1){
            console.log("cant add another point");
            toggle_function("line")
          }

          else {
          // Because path is an MVCArray, we can simply append a new coordinate
          // and it will automatically appear.
              path.push(event.latLng);
              if(path.getLength() > 1){
                console.log("finished line");
                toggle_function("line");
                }
          }
        }

        else{
            var icon = {
            url:"/static/NRTC/" + currentFunction + ".png",
            scaledSize:new google.maps.Size(40,40)
            }

            console.log(event);
            console.log(event.latLng);
            var first = true;
            for (var i = 0;i<markerArray.length;i++){
                if (markerArray[i]["itemType"] == currentFunction && markerArray[i]["marker"].map){
                    first = false;
                    break;
                }

            }
            markerDict=create_marker(icon,"","",event.latLng.lat(),event.latLng.lng(),currentFunction,first,"Walk");
            markerDict["id"] = null;
            markerDict["itemType"] = currentFunction;
            markerDict["first"] = first;
            markerArray.push(markerDict);
            toggle_function(currentFunction);
        }


    }

}


function openTextModal(evt) {
    // Get the modal

    console.log("line is" + line);
    if(!line ){
        alert("You need to draw a line showing where the\n actual count point is");
        return;
    }

    var path = line.getPath();
    if(path.getLength() < 2){
        alert("You have only added 1 point to the line");
        return;
    }
    var standout = false;
    var park = false;
    for (i = 0;i< markerArray.length;i++){
        if(markerArray[i]["itemType"] == "parking" && markerArray[i]["marker"].map){
            park=true;
        }
        if(markerArray[i]["itemType"] == "standout" && markerArray[i]["marker"].map){
            standout=true;
        }
    }
    if (!park){
        alert("You need to have at least 1 parking location");
        return;
    }

    if (!standout){
        //alert("You need to have at least 1 standout location");
        //return;
    }

    var modal = document.getElementById('textModal');

    var span = document.getElementsByClassName("textclose")[0];


    modal.style.display = "block";


    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}



function saveMapData(){
    var asPerSRef = document.querySelector('input[name="sRef"]:checked');

    if (!asPerSRef){
        alert("You must indicate whether count point is as per sRef")
        return
    }
    console.log("sref " + asPerSRef.value);
    var modal = document.getElementById('textModal');
    modal.style.display = "none";
    var path = line.getPath();
    lineData = [];
    for(i=0;i<path.getLength();i++){
        lineData.push(line.getPath().getAt(i));
    }
    lineInfo = CPMarker.infoWindow.getContent().getElementsByTagName("textarea")[0].value
    markers = [];
    for (i = 0;i< markerArray.length;i++){
        if (markerArray[i]["itemType"] != "hospital" && markerArray[i]["itemType"] != "military"
        && markerArray[i]["itemType"] != "roadworks"
        && markerArray[i]["itemType"] != "plannedroadworks"
        ){
            marker = markerArray[i];
            console.log(marker["permissions"]);
            console.log(typeof marker["permissions"]);
            console.log(marker["marker"].getPosition()["lat"]);
            if(marker.marker.map === null){
                console.log("detected marker of type " + marker["itemType"] + " to be deleted");
                marker["itemType"] = "Deleted";
            }
            if(marker["permissions"]){
                permissions = marker["permissions"].value;
            }
            else{
                permissions = "";
            }
            if (marker["itemType"] == "toilet" || marker["itemType"] == "food"){
                var select = marker["window"].getContent().getElementsByTagName("select")[0];
                var option = select.options[select.selectedIndex].text;
            }
            else{
                var option = "";
            }
            markers.push([marker["id"],marker["marker"].getPosition(),marker["info"].value,permissions,marker["itemType"],marker["first"],option])
        }
    }

    $.ajax({
		type: "POST",
		url: "/nrtc/saveItemsOfInterest",

		//url:"https://tads.tracsis.com/dm/server/get-jobs.php",
		data: JSON.stringify({"markers":markers,"lineData":lineData,"sRef":asPerSRef.value,"lineInfo":lineInfo}),
		dataType: "json",
		contentType: "application/json; charset=utf-8",
		traditional: true,

		success: function (response) {
		    console.log("OH NO");
			console.log(response);
            console.log("aero")
			if (response.error) {
				displayMessage('msg-error', response.error);
			} else {
				var data = response;
                console.log("receive data");
				console.log(response);
				//initMap(response);
				window.location = 'getNetworkInfo';

			}
		},
		error: function(textStatus, errorThrown) {
		    console.log("OH YES");
			console.log(textStatus);
			return {"centre":[],"items":{}}
		}
	});


}






function toggle_primary(marker,itemType){
    checkboxes = document.getElementsByClassName("checkbox-"+itemType);
    for (var i=0;i<markerArray.length;i++){
        if (markerArray[i]["itemType"] == itemType && markerArray[i]["marker"] !== marker){
            console.log("found marker ");
            content = markerArray[i]["window"].getContent();
            var ele = content.getElementsByClassName("checkbox-"+itemType)[0];
            ele.disabled = false;
            ele.checked = false;
            console.log(ele);
            markerArray[i]["first"] = false;
        }
        if (markerArray[i]["marker"] == marker){
            console.log("identified correct marker");
            content = markerArray[i]["window"].getContent();
            var ele = content.getElementsByClassName("checkbox-"+itemType)[0];
            ele.disabled = false;
            ele.checked = true;
            ele.disabled = true;
            markerArray[i]["first"] = true;
        }
    }
}


function create_marker(icon,infoText,permissionsText,lat,lon,itemType,first,accessMethod){
            console.log("creating marker of type" + icon);
            var draggable = false;
            if (itemType !== "hospital" && itemType !== "military" && itemType !== "roadworks" && itemType !== "plannedroadworks"){
                draggable=true;
            }
            var marker = new google.maps.Marker({position:{lat:lat,lng:lon},
                                            icon:icon,
                                            draggable:draggable,
                                            map:map
                                            });
            outerdiv = document.createElement("div");

            if(itemType == "parking" | itemType == "toilet" | itemType == "food" | itemType== "standout"){
                span = document.createElement("span");
                span.innerText = "Primary";
                outerdiv.appendChild(span);
                div = document.createElement("div");
                var checkbox = document.createElement('input');
                checkbox.type = "checkbox";
                checkbox.name = "checkbox-"+itemType;
                checkbox.className = "checkbox-"+itemType;
                if (first){
                    checkbox.checked=true;
                    checkbox.disabled=true;
                }
                checkbox.onclick = function() {
                    toggle_primary(marker,itemType);
                };
                //checkbox.value = "value";
                //checkbox.id = "id";
                div.appendChild(checkbox);
                outerdiv.appendChild(div);
            }

             if(itemType == "food" | itemType == "toilet"){
                div = document.createElement("div");
                var select = document.createElement("select");
                var option = document.createElement("option");
                option.text = "Walk";
                select.add(option);
                var option = document.createElement("option");
                option.text = "Drive";
                select.add(option);
                select.value = accessMethod;
                div.appendChild(select);
                outerdiv.appendChild(div);
             }

            if(itemType !== "roadworks" && itemType !== "plannedroadworks"){

                span = document.createElement("span");
                span.innerText = "Info";
                outerdiv.appendChild(span);
                div = document.createElement("div");
                info = document.createElement("textarea");
                info.value = infoText;
                info.cols = 30;
                info.rows = 4;
                div.appendChild(info);
                outerdiv.appendChild(div);
            }
            else{
                var table = document.createElement("table");
                table.className = "table-style-three";
                //infotext in this case is a dictionary
                for (var key in infoText){
                    var tr = document.createElement("tr");
                    var th = document.createElement("th");
                    var td = document.createElement("td");
                    th.innerText = key;
                    td.innerText = infoText[key];
                    tr.appendChild(th);
                    tr.appendChild(td);
                    table.appendChild(tr);
                }
                //outerdiv.appendChild(table)
                outerdiv = infoText; //= new DOMParser().parseFromString(infoText, 'text/html') ;
            }


            if(itemType == "parking" | itemType == "toilet" | itemType == "standout"){
                span = document.createElement("span");
                span.innerText = "Permissions(if req)";
                outerdiv.appendChild(span);
                div = document.createElement("div");
                var permissions = document.createElement("textarea");
                permissions.value = permissionsText;
                permissions.cols = 30;
                permissions.rows = 4;

                div.appendChild(permissions);
                outerdiv.appendChild(div);
            }


            if(itemType !== "roadworks"){
                div = document.createElement("div");
                var el = document.createElement("button");
                el.name = "delete";
                el.type = "button";
                el.innerHTML = "Delete Marker"
                el.onclick = function() {
                    delete_marker(marker,itemType);
                };
                div.appendChild(el);
                outerdiv.appendChild(div);
            }
            var infoWindow = new google.maps.InfoWindow({
                    content:outerdiv,
                    marker:marker,
                });
            marker.addListener('click', function() {
                    infoWindow.open(map, marker);
                  });

            return {"marker":marker,"info":info,"permissions":permissions,"type":itemType,"window":infoWindow}
}

function mark_as_home_safe(){

getLocation();

}


function getLocation() {
    if (navigator.geolocation) {
        var pos = navigator.geolocation.getCurrentPosition();
        console.log(pos);
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}



function get_map(){
    var CPNo = '<%=Session["CPNo"]%>';
    console.log(CPNo);
    $.ajax({
		type: "POST",
		url: "/nrtc/getItemsOfInterest",

		//url:"https://tads.tracsis.com/dm/server/get-jobs.php",
		dataType: "json",
		contentType: "application/json; charset=utf-8",
		traditional: true,

		success: function (response) {
		    console.log("OH NO");
			console.log(response);
            console.log("aero")
			if (response.error) {
				displayMessage('msg-error', response.error);
			} else {
				var data = response;
                console.log("receive data");
				console.log(response);
			    initMap(response);
			}
		},
		error: function(textStatus, errorThrown) {
		    console.log("OH YES");
			console.log(textStatus);
			return {"centre":[],"items":{}}
		}
	});
}