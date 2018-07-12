import requests
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pyproj import Proj, transform,Geod
import datetime

heightOffset = 1000
widthOffset =  1000

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

def get_extent(payload):
    r = requests.post("http://www.roadworksscotland.org/Home/GetWorksInExtent", data=payload)
    print(r)
    return json.loads(r.text)

def get_detail(LARef):
    data = {"laref": LARef}
    r = requests.post("https://www.roadworksscotland.org/Home/GetFeatureDetails",data=data)
    result = json.loads(r.text)
    keys = ["LARef","StartDate","EndDate","PromoterName","WorksReference","PromoterTel1"]
    headers = ["LARef","Start Date","End Date","Promoter Name","Works Reference","Phone No"]
    info = {headers[index]:result[key] for index,key in enumerate(keys)}
    #info = "\n".join([key + ": " + value for key,value in info.items()])
    return info

def get_dist(p1,p2):
    geod = Geod(ellps="WGS84")
    _, _, dist = geod.inv(p1[1], p1[0], p2[1], p2[0])
    return dist

def get_all_roadworks_for_lat_lon(centre,startDate,endDate):
    #centre = [55.928469, -3.505401]
    converted_centre = convert_from_4326_to_1936(centre)
    xmin, ymax = [converted_centre[0] - widthOffset, converted_centre[1] + heightOffset]
    xmax, ymin = [converted_centre[0] + widthOffset, converted_centre[1] - heightOffset]
    #payload = {"xmax":xmax,"xmin":xmin,"ymax":ymax,"ymin":ymin}#,"lowImpactLayer":False,"mediumImpactLayer":True,"highImpactLayer":True,"roadClosuresLayer":True,"startDate":startDate,"endDate":endDate}
    #print("payload is", payload)
    #payload = "MinX=" + str(xmin) + "&MinY=" + str(ymin) + "&MaxX=" + str(xmax) + "&MaxY=" + str(ymax)
    payload = {"MinX":313530.940750824,"MinY":756505.9528389294,"MaxX":314413.98939192126,"MaxY":757097.2977716192}#"#&Filter%5BExtent%5D=%5Bobject+Object%5D&Filter%5BFromDate%5D=26%2F04%2F2018&Filter%5BToDate%5D=03%2F05%2F2018&Filter%5BRoadClosures%5D=true&Filter%5BHighImpactWorks%5D=true&Filter%5BMediumImpactWorks%5D=true&Filter%5BLowImpactWorks%5D=true"
    result = get_extent(payload)
    print("result is",result)
    roadworks = []
    for item in result:
        coords = convert_from_1936_to_4326([item["Easting"],item["Northing"]])
        info = get_detail(item["LARef"])
        #print(info)###
        dist = get_dist(centre,coords)
        info["Distance"]= str(round(dist,0)) + "m"
        roadworks.append({"lat":coords[0],"info":info,"permissions":"","lon":coords[1],"itemType":"roadworks"})
    return roadworks


centre = [55.928469, -3.505401]





#startDate = datetime.datetime.now().date()
#endDate = (startDate + datetime.timedelta(days=7)).strftime("%d/%m/%Y")
#startDate =startDate.strftime("%d/%m/%Y")
#result = get_all_roadworks_for_lat_lon(centre,startDate,endDate)
#roadworks = []
#for item in result:
#    coords = convert_from_1936_to_4326([item["Easting"],item["Northing"]])
#    info = get_detail(item["LARef"])
#    print(info)###

#    dist = get_dist(centre,coords)
#    info += "\nDistance: " + str(round(dist,0))
#    roadworks.append({"lat":coords[0],"text":info,"lon":coords[1],"itemType":"roadworks"})
