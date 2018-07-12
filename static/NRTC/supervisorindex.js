
var mouseX = 0;
var mouseY = 0;
var selectedFilterElement;
var filterList = [];

$(document).mousemove( function(e) {
    mouseX = e.pageX;
    mouseY = e.pageY;
});
$(document).mousedown(function(e) {
    var ddmenu = $('#ddmenu');

    if (!ddmenu.is(e.target) && ddmenu.length && ddmenu.has(e.target).length === 0) {
        ddmenu.remove();
    }
});


function set_filters(){
    var headers = document.getElementById("header-table");
    for (i=0;i<headers.rows[1].length;i++){
           var el = headers.rows[1].cells[i];
           console.log(el);
           el.addEventListener("click",function(e){
             alert(e.target+" clicked");
            });

    }

 }


 function getList(columnName) {
	if ($('#ddmenu').length) {
		$('#ddmenu').remove();
	}

     var token =  $('input[name="csrfmiddlewaretoken"]').attr('value');

    console.log("whjpopo");
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }


    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", token);
            }
        }
    });



	$.ajax({
		type: "POST",
		url: "/nrtc/getColumnValues",
		data: JSON.stringify({"filters":filterList,"column":columnName}),
		dataType: "json",
		contentType: "application/json; charset=utf-8",
		traditional: true,
		success: function (response) {
			console.log(response);
			if (response.error) {
				console.log('msg-error', response.error);
			} else {
				var data = response.data;
				var columnValues = "";
				if (data.hasOwnProperty("columnValues")) {
					columnValues = data['columnValues'];
				}
				$('body').append("<div id='ddmenu'></div>");
				$('#ddmenu').html("<ul>" +
					"<li onclick='removeFilter(\"" + columnName + "\")'>[ Show All ]</li>" +
					"<li onclick='removeBlanks(\"" + columnName + "\")'>[ Remove Blanks ]</li>" +
					"<li onclick='onlyBlanks(\"" + columnName + "\")'>[ Only Blanks ]</li>" +
					"<li onclick='sortBy(\"" + columnName + "\", \"ASC\")'>[ Sort Ascending ]</li>" +
					"<li onclick='sortBy(\"" + columnName + "\", \"DESC\")'>[ Sort Descending ]</li>" +
					"<li onclick='removeSort(\"" + columnName + "\")'>[ Remove Sort ]</li>" +
					"<li>[ Search ] <input class='search-input' type='text' onkeyup='searchString(this)' /></li>" +
					columnValues +
					"</ul>");
                 console.log("x,y",mouseX,mouseY);
				if ((mouseX + $('#ddmenu').width()) > $(window).width()) {
					$('#ddmenu').css({
						left: $(window).width() - $('#ddmenu').width() - 2,
						top: mouseY - 120
					});
				} else {
					$('#ddmenu').css({
						left: mouseX - 20,
						top: mouseY - 20
					});
				}
			}
		},
		error: function(textStatus, errorThrown) {
		    console.log("OH YES");
			console.log(textStatus);
			console.log('msg-error', "Error[005] - Unable to get Filter List");
		}
	});
}


function searchString(obj) {
	if ($('#ddmenu').length) {
		var value = obj.value.toLowerCase();
		var listArray = [];
		$('#ddmenu li').each(function (index) {
			if (index > 6) {
				if ($(this).hasClass('nodisplay')) {
					$(this).removeClass('nodisplay');
				}

				var itemValue = $(this).html();
				if (itemValue.toLowerCase().indexOf(value) === -1) {
					$(this).addClass('nodisplay');
				} else {
					listArray.push(itemValue);
				}
			}
		});
	}
}



function removeFilter(columnIndex) {
	if ($('#ddmenu').length) {
		$('#ddmenu').remove();
	}

	if (columnIndex) {
		if (filterList) {
			for (var f = 0; f < filterList.length; f++) {
			    console.log("looking at",filterList[f],columnIndex,parseInt(filterList[f].column) === parseInt(columnIndex));
				if (parseInt(filterList[f].column) === parseInt(columnIndex)) {
				    console.log("wooo~");
				    var filterElems = document.getElementsByClassName("filter");
				    filterElems[parseInt(columnIndex) - 1].innerHTML = "[filter]";
					if (filterList.length - 1 > 0) {
						filterList.splice(f, 1);
					} else {
						filterList = [];
						break;
					}
				}
			}

			updateTable();
		}
	}
}




function filterBy(columnIndex, value) {
	if ($('#ddmenu').length) {
		$('#ddmenu').remove();
	}


    if (!filterList) {
			filterList = [{"column":columnIndex,"value":value}];
		} else {
			var match = false;
			for (var f = 0; f < filterList.length; f++) {
				if (filterList[f].column === columnIndex) {
					filterList[f].value = value;
					match = true;
					break;
				}
			}
			if (!match) {
				filterList.push({"column":columnIndex,"value":value});
			}
		}

		var filterElems = document.getElementsByClassName("filter");
		for (var f = 0; f < filterList.length; f++) {
	        index = parseInt(filterList[f].column) - 1;
			filterElems[index].innerHTML = "[" + filterList[f].value + "]";
		}

    updateTable();
}

function updateTable(){
     var token =  $('input[name="csrfmiddlewaretoken"]').attr('value');

    console.log(token);
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }


    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", token);
            }
        }
    });

	$.ajax({
		type: "POST",
		url: "/nrtc/filter",
		data: JSON.stringify({"filters":filterList}),
		dataType: "json",
		contentType: "application/json; charset=utf-8",
		traditional: true,
		success: function (response) {
			console.log(response);
			if (response.error) {
				console.log('msg-error', response.error);
			} else {
			    var filterElems = document.getElementsByClassName("filter");
			    //index = parseInt(columnIndex);
			    //filterElems[index].innerHTML = "[" + value + "]";
			    data = response["data"];
				var table = document.getElementById("data-table");
				table.innerHTML = "";
				for(var i=0;i<data.length;i++){
				    var row = document.createElement("tr");
				    table.appendChild(row);
				    for(var col =0;col< data[i].length - 1;col++){
				        var td = document.createElement("td");
				        td.innerHTML = data[i][col];
				        if(col==0){
				            td.classList.add("w1");
				        }
				        else{
				            td.classList.add("w3");
				        }
				        row.appendChild(td);
				    }
				    td = document.createElement("td");
				    td.classList.add("w1");
				    row.appendChild(td);
				    var button = document.createElement("button");
				    button.classList.add("button");
				    var projectNo = data[i][data[i].length-1];

				    var func = (function(projectNo){
                         return function(){ window.location.assign("/nrtc/viewProject/" + projectNo)};
                    })(projectNo);

				    button.onclick= func;
				    button.innerHTML = "View";
				    td.appendChild(button);
				}
			}
		},
		error: function(textStatus, errorThrown) {
		    console.log("OH YES");
			console.log(textStatus);
			console.log('msg-error', "Error[005] - Unable to get Filter List");
		}
	});
}

