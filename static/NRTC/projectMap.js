
var map;


function build_project_details_table(data){
    var outerdiv = document.createElement("div");
    var table = document.createElement("table");
    table.className = "table-style-three";
    for (i=0;i<data.length;i++){
        var key = data[i][0];
        var value = data[i][1];
        console.log(key,value);
        var tr = document.createElement("tr");
        var th = document.createElement("th");
        var td = document.createElement("td");
        th.innerText = key;
        td.innerText = value;
        tr.appendChild(th);
        tr.appendChild(td);
        table.appendChild(tr);
    }
    outerdiv.appendChild(table);
    return outerdiv;


}


function initMap(data) {
   console.log("after get map call");


   var centre=[54.596186, -2.288501];

   map = new google.maps.Map(document.getElementById('map'), {
        zoom: 6,
        draggableCursor:'default',
        center: {lat: centre[0], lng: centre[1]}  // Center the map on Chicago, USA.
   });
    //console.log("here",data.length);

    for (i=0;i<data.length;i++){
        //console.log("item",i);
        var proj = data[i];
        var centre = proj[0];
        //console.log(centre);
        //console.log(proj.slice(1));
        var outerdiv = document.createElement("div");
        var table = document.createElement("table");
        table.className = "table-style-three";
        for (j=0;j<proj.slice(1).length;j++){
            var key = proj.slice(1)[j][0];
            var value = proj.slice(1)[j][1];
            var tr = document.createElement("tr");
            var th = document.createElement("th");
            var td = document.createElement("td");
            th.innerText = key;
            td.innerText = value;
            tr.appendChild(th);
            tr.appendChild(td);
            table.appendChild(tr);
            }
            outerdiv.appendChild(table);
            div = document.createElement("div");
                var el = document.createElement("button");
                el.name = "delete";
                el.type = "button";
                el.innerHTML = "View"
                //console.log("location.href='/nrtc/viewProject/" + String(proj[1][1]) + "';");
                el.onclick = new Function('event',"location.href='/nrtc/viewProject/" + String(proj[1][1]) + "';");
                div.appendChild(el);
                outerdiv.appendChild(div);


        var marker = new google.maps.Marker({position:{lat:centre[0],lng:centre[1]},
                                            draggable:false,
                                            map:map
                                            });

        var infoWindow = new google.maps.InfoWindow({
                    content:outerdiv
                });

            marker.addListener('click', (function(marker,outerdiv,infowindow){
                return function() {
                    infowindow.setContent(outerdiv);
                    infowindow.open(map,marker);
                };
            })(marker,outerdiv,infoWindow));

    }
    console.log("now here");
}

get_map();














function get_map(){
    var CPNo = '<%=Session["CPNo"]%>';
    console.log(CPNo);
    //return
    $.ajax({
		type: "POST",
		url: "/nrtc/getProjectMap",

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
			    initMap(response["data"]);
			}
		},
		error: function(textStatus, errorThrown) {
		    console.log("OH YES");
			console.log(textStatus);
			return {"centre":[],"items":{}}
		}
	});
}