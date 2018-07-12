var map;
var markerArray = [];
itemTypes = ["toilet", "food", "school","parking","standout","warning","hospital","military"];


/***************************************************************************************

    Functions to deal with ??????

****************************************************************************************/







function openTab(evt, tabName) {
  var i, x, tablinks;
  console.log(tabName + " clicked");
  console.log(document.getElementById(tabName));
  x = document.getElementsByClassName("tab");
  for (i = 0; i < x.length; i++) {
      x[i].style.display = "none";
      console.log(x[i].id);
  }
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < x.length; i++) {
      tablinks[i].style.backgroundColor = "#1c2674";
  }
  document.getElementById(tabName).style.display = "flex";
  evt.target.style.backgroundColor = "red";
  localStorage.setItem("visibleTab", evt.target.id);
}









/***************************************************************************************

    Functions to deal with roadworks checks etc

****************************************************************************************/

function notifyRoadworks(){
    var selected = []
    for(var i =0;i<markerArray.length;i++){
        if (markerArray[i]["itemType"] == "roadworks" || markerArray[i]["itemType"] == "plannedroadworks"){
            //console.log(markerArray[i]["marker"]);
            var content = markerArray[i]["marker"].infoWindow.getContent();
            var chk = content.getElementsByClassName("notify-checkbox")[0];
            console.log(chk.checked);
            if (chk.checked){
                console.log("id of checked is",markerArray[i]["id"]);
                selected.push(markerArray[i]["id"])
            }
        }
    }
}

function searchRoadworks(){
    console.log("searching");
    $.ajax({
		type: "POST",
		url: "/nrtc/searchRoadworks",

		data:JSON.stringify({"form":$("#search-form").serializeArray()}),
		dataType: "json",
		contentType: "application/json; charset=utf-8",
		traditional: true,
		success: function (response) {
		    console.log(response);
            initMap(response);
		},
		error: function(textStatus, errorThrown) {
		    alert("Search failed");
		}
	});
}

var line;


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
   var lineData = data["lineData"];
   console.log("no of items" ,lineData["coords"]);
   console.log(centre.length);
   if (centre.length > 0){
      map = new google.maps.Map(document.getElementById('map'), {
        zoom: 14,
        draggableCursor:'default',
        center: {lat: centre[0], lng: centre[1]}  // Center the map on Chicago, USA.
      });

      map.addListener('zoom_changed', function() {

        console.log("zoom is now",map.zoom);
        var zoomLevel = document.getElementById("zoom-level");
        zoomLevel.value = map.zoom;

        });


      }
  var marker = new google.maps.Marker({position:{lat:centre[0],lng:centre[1]},

                                            draggable:false,
                                            map:map
                                            });

    var div = document.getElementsByClassName("count-point-div")[0];
   console.log("------------------------------------------------");
    console.log(div);
   var infoWindow = new google.maps.InfoWindow({
                    content:div,
                });
            marker.addListener('click', function() {
                    var div = infoWindow.getContent();
                    div.style.display = "block";
                    infoWindow.open(map, marker);
                  });

  google.maps.event.addListener(map,'click', function(event) {
    console.log(event.latLng.lat());
    map_clicked(event);
  });
  for (var i = 0; i < items.length; i++) {
    var icon = {
            url:"/static/NRTC/" + items[i]["itemType"] + ".png",
            scaledSize:new google.maps.Size(40,40)
            }
   markerDict = create_marker(icon,items[i]["info"],items[i]["permissions"],items[i]["lat"],items[i]["lon"],items[i]["itemType"]);
   markerDict["id"] = items[i]["id"];
   markerDict["itemType"] = items[i]["itemType"]
   markerArray.push(markerDict);

}
console.log(lineData["coords"]);
if (lineData["coords"]){
        console.log("in line create");
        line = new google.maps.Polyline({
                editable: false,
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2,
                map: map
              });

        for(i=0;i<lineData["coords"].length;i++){
            line.getPath().push(new google.maps.LatLng(lineData["coords"][i]));

        }
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


function delete_marker(marker){
    console.log("rceived");
    console.log(marker)
    marker.setMap(null);
    console.log("marker map is"  + marker.map);

}


function toggle_function(action){
    console.log("in toggle function");
    el = document.getElementById(action);
    console.log("action is",action);
    console.log("current function is",currentFunction);
    console.log("el is",el);
    if (currentFunction === undefined){
        console.log("not assigned an action yet");
        currentFunction = action;
        console.log("user toggled on action " + currentFunction);
        document.body.style.cursor = 'crosshair';
        map.set("draggableCursor",'crosshair');
        el.style["boxShadow"] = null;
        el.style["boxShadow"] = "0px 0px 35px rgba(255, 0, 255, 0.9)";
    }
    else{
        console.log("user clicked " + action);
        console.log("currently doing action " + currentFunction);
        if (currentFunction === "line" & line !== undefined) {
            var path = line.getPath();
            var lineLength = path.getLength();
            if (action !== "line" & lineLength < 2){
                console.log("deleting line");
                 line.setMap(null);
                 line = undefined;
                 el = document.getElementById("line");
                 el.style.boxShadow = null;
                 currentFunction = action;
            }
            if (action === "line" & lineLength ===2){
                console.log("finished line");
                el = document.getElementById("line");
                 el.style.boxShadow = null;
                 currentFunction = undefined;
                 document.body.style.cursor = 'default';
                map.set("draggableCursor",'default');
            }
        }

        else{
            console.log("user toggled off action " + currentFunction);
            var el = document.getElementById(currentFunction);
            console.log(el);
            console.log(el.style.boxShadow);
            el.style.boxShadow = null;

            if (action !== currentFunction){
                console.log("user selected different functionsdsgsgsgs");
                el = document.getElementById(action);
                el.style["boxShadow"] = null;
                el.style["boxShadow"] = "0px 0px 35px rgba(255, 0, 255, 0.9)";
                currentFunction = action;
                console.log("setting crosshairs");
                document.body.style.cursor = 'crosshair';
                map.set("draggableCursor",'crosshair');
                console.log(map.get("draggableCursor"));
            }
            else{
                console.log("setting to undefined");
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
            markerDict=create_marker(icon,"","",event.latLng.lat(),event.latLng.lng(),currentFunction);
            markerDict["id"] = null;
            markerDict["itemType"] = currentFunction;
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
    markers = [];
    for (i = 0;i< markerArray.length;i++){
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
        markers.push([marker["id"],marker["marker"].getPosition(),marker["info"].value,permissions,marker["itemType"]])
    }


    var CPNo = '<%=Session["CPNo"]%>';
    console.log(CPNo);
    $.ajax({
		type: "POST",
		url: "/nrtc/saveItemsOfInterest",

		//url:"https://tads.tracsis.com/dm/server/get-jobs.php",
		data: JSON.stringify({"markers":markers,"lineData":lineData,"sRef":asPerSRef.value}),
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

function download_pdf(){
    var CPNo = '<%=Session["CPNo"]%>';
    console.log("getting pdf");
    window.location.href = 'nrtc/downloadPdf/' + String(CPNo);

}

function create_marker(icon,infoText,permissionsText,lat,lon,itemType){
            //console.log("creating marker of type" + icon);
            //console.log(lat);
            //console.log(lon);
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
            if(itemType !== "roadworks" && itemType !== "plannedroadworks" ){

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
                var parser = new DOMParser();
                var outerdiv = parser.parseFromString(infoText,"text/html");
                outerdiv = outerdiv.getElementsByTagName("div")[0];
                console.log(outerdiv);
                info = "";
            }


            if(itemType !== "warning" & itemType !== "info" & itemType !== "roadworks" & itemType !== "plannedroadworks"){
                span = document.createElement("span");
                span.innerText = "Permissions";
                outerdiv.appendChild(span);
                div = document.createElement("div");
                var permissions = document.createElement("textarea");
                permissions.value = permissionsText;
                permissions.cols = 30;
                permissions.rows = 4;

                div.appendChild(permissions);
                outerdiv.appendChild(div);
            }


            //if(itemType !== "roadworks"){
                //div = document.createElement("div");
               // var el = document.createElement("button");
               // el.name = "delete";
               // el.type = "button";
               // el.innerHTML = "Delete Marker"
               // el.onclick = function() {
                   //delete_marker(marker);
                //};
                //div.appendChild(el);
               // outerdiv.appendChild(div);
            //}
            var infoWindow = new google.maps.InfoWindow({
                    content:outerdiv,
                });
            marker.addListener('click', function() {
                    infoWindow.open(map, marker);
                  });
            marker.infoWindow = infoWindow;
            return {"marker":marker,"info":info,"permissions":permissions}
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


