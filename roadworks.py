import requests
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pyproj import Proj, transform,Geod
import datetime


def convert_from_3857_to_4326(coords):
    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')
    x1, y1 = coords
    x2, y2 = transform(inProj, outProj, x1, y1)
    return (y2,x2)

def convert_from_4326_to_3857(coords):
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:3857')
    x1, y1 = coords
    x2, y2 = transform(inProj, outProj, y1, x1)
    return (x2,y2)

def convert_from_4326_to_1936(coords):
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:27700')
    x1, y1 = coords
    x2, y2 = transform(inProj, outProj, y1, x1)
    return (x2, y2)

def convert_from_1936_to_4326(coords):
    inProj = Proj(init='epsg:27700')
    outProj = Proj(init='epsg:4326')
    x1, y1 = coords
    x2, y2 = transform(inProj, outProj, x1, y1)
    return (y2, x2)

heightOffset = 4000
widthOffset =  4000

incidents = ["incidents_live_incident",
            "incidents_live_hgvclosure",
            "incidents_live_laneclosure",
            "incidents_live_roadclosure",
            "incidents_live_landslip",
            "incidents_live_flood",
             "TM_LAYER_ROADCLOSURE_LIVE"
             ]


def get_postcode(lat,lon):
    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + str(lat) + "," + str(lon) + "&sensor=true_or_false&key=AIzaSyDRVvMxvveTE7ladKBhUnptw9-lOoHMAAU"
    #print(url)
    r = requests.get(url)
    #print(r.json())
    result = r.json()
    for item in result["results"][0]["address_components"]:
        # print(item["types"][0])
        if item["types"][0] == "route":
            road = item["long_name"]
        if item["types"][0] == "postal_code":
            postcode = item["long_name"]

            return postcode
    return ""

def get_postcode_from_1936(easting,northing):
    coords =convert_from_1936_to_4326((easting,northing))
    return get_postcode(coords[0],coords[1])


def get_dist(p1,p2):
    geod = Geod(ellps="WGS84")
    _, _, dist = geod.inv(p1[1], p1[0], p2[1], p2[0])
    return dist

def get_extent(payload):
    r = requests.get("https://portal.roadworks.org/json/qry_mapLayerData2.cfm?" + payload)
    #print(r.status_code)
    #print(r.cookies)
    return r.json()

def get_detail(id):
    r = requests.get("https://portal.roadworks.org/json/qry_getIncidentDetail.cfm?se_id="+str(id))
    #print(r.status_code)
    #print(r.text)
    result = r.json()
    keys = ["start_date_display","end_date_display","promoter","impact_desc"]
    headers = ["Start Date","End Date","Promoter Name","Impact"]
    info = {headers[index]:result[key] for index,key in enumerate(keys)}
    #info = "\n".join([key + ": " + value for key,value in info.items()])
    coords = convert_from_1936_to_4326((result["easting"],result["northing"]))
    return (result,coords)

def get_all_roadworks_for_lat_lon(centre,startDate,endDate):
    #centre = [53.410811, -1.377244]
    converted_centre = convert_from_4326_to_1936(centre)
    #converted_centre = []
    xmin, ymax = [converted_centre[0] - widthOffset, converted_centre[1] + heightOffset]
    xmax, ymin = [converted_centre[0] + widthOffset, converted_centre[1] - heightOffset]
    #print(xmin,ymin,xmax,ymax)
    payload  = "sw_lon=" + str(xmin) + "&sw_lat=" + str(ymin) + "&ne_lon=" + str(xmax) + "&ne_lat=" + str(ymax) + "&gr=bng&filterstartdate=" + startDate.strftime("%d/%m/%Y") + "&filterenddate=" + endDate.strftime("%d/%m/%Y") + "&user_id=1&organisation_id=1&lyrs=" + ",".join([i.upper() for i in incidents])
    #payload = "sw_lon=441548&sw_lat=384751&ne_lon=444084&ne_lat=388298&gr=bng&filterstartdate=27/03/2018&filterenddate=27/03/2018&user_id=1&organisation_id=1&lyrs=INCIDENTS_LIVE_INCIDENT,INCIDENTS_LIVE_ACCIDENT,INCIDENTS_LIVE_TRAFFIC_CONGESTION,INCIDENTS_LIVE_WEATHER,INCIDENTS_LIVE_LANDSLIP,INCIDENTS_LIVE_FLOOD,INCIDENTS_LIVE_ROADCLOSURE,INCIDENTS_LIVE_LANECLOSURE,INCIDENTS_LIVE_HGVCLOSURE"
    result = get_extent(payload)
    #print(result)
    roadworks = []
    for key,item in result.items():
        #print(item)
        if len(item["features"]) > 0:
            #print(item["features"])
            for feature in item["features"]:
                print(feature["linked_id"])
                info,coords = get_detail(feature["linked_id"])
                #print("info")
               #coords = [feature["lat"],feature["lon"]]
                #print(info)###
                dist = get_dist(centre,coords)
                info["Distance"] =str(round(dist,0)) + "m"
                roadworks.append({"lat":coords[0],"info":build_popup_window(info),"permissions":"","lon":coords[1],"itemType":"roadworks","id":feature["linked_id"]})
    return roadworks

def build_popup_window(info):
    s = "<div><div><input type='checkbox' class='notify-checkbox'>Notify</div>\n<div class='iframepoint'>\n    <h1 id=\'popup\'>Roadwork</h1><table cellspacing='0'>\r\n\t"
    for key,item in info.items():
        s+="<tr>\r\n\t\t\r\n\t\t<td class='field'><strong>" + key + "</strong></td><td>" + str(item) + "</td>\r\n\t"
    s+="\r\n</table>\n</div></div>"
    return s


payload = "sw_lon=297999&sw_lat=639320&ne_lon=351215&ne_lat=706102&gr=bng&mapzoom=11&filterstartdate=26/03/2018&filterenddate=26/03/2018&user_id=1&organisation_id=1&lyrs=INCIDENTS_LIVE_INCIDENT,INCIDENTS_LIVE_ACCIDENT,INCIDENTS_LIVE_TRAFFIC_CONGESTION,INCIDENTS_LIVE_WEATHER,INCIDENTS_LIVE_LANDSLIP,INCIDENTS_LIVE_FLOOD,INCIDENTS_LIVE_ROADCLOSURE,INCIDENTS_LIVE_LANECLOSURE,INCIDENTS_LIVE_HGVCLOSURE&mode=v7"

#result = get_detail("105254920")
#print(result)
#exit()
#centre = [52.75272994299409,0.39394100464269816]
#startDate = datetime.datetime.now().date()
#endDate = (startDate + datetime.timedelta(days=7)).strftime("%d/%m/%Y")
#startDate = startDate.strftime("%d/%m/%Y")
#result = get_all_roadworks_for_lat_lon(centre,startDate,endDate)
#print(result)
#for key,item in result.items():
#    print(key,item["features"])