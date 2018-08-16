from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,JsonResponse,Http404,HttpResponseRedirect
import json
from NRTC.models import *
from django.views.decorators.csrf import csrf_exempt,ensure_csrf_cookie
import django.core.exceptions
from django.core.files.storage import default_storage
import pandas as pd
from django.template import loader, Context
from django.conf import settings
from functools import wraps
from signpad2image.signpad2image import s2if

from pyproj import Proj, transform,Geod
import time
import NRTC.roadworkscotland
import NRTC.roadworks
import NRTC.trafficscotland
import datetime
import smopy
from PIL import Image,ImageDraw,ImageFont
import os

import PyPDF2

import io
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

tfcGrading = {1:[8,6],2:[6,4],3:[4,2],4:[3,2],5:[3,2],6:[2,1],7:[2,1]}
itemTypes = ["toilet", "food", "school","parking","standout","warning","hospital","military"]

def require_https(view):
    """A view decorator that redirects to HTTPS if this view is requested
    over HTTP. Allows HTTP when DEBUG is on and during unit tests.

    """

    @wraps(view)
    def view_or_redirect(request, *args, **kwargs):
        print("HERE!!!!")
        if not request.is_secure():
            # Just load the view on a devserver or in the testing environment.
            if settings.DEBUG or request.META['SERVER_NAME'] == "testserver":
                return view(request, *args, **kwargs)

            else:
                # Redirect to HTTPS.
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)

        else:
            # It's HTTPS, so load the view.
            return view(request, *args, **kwargs)

    return view_or_redirect



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


def get_dist(p1,p2):
    geod = Geod(ellps="WGS84")
    _, _, dist = geod.inv(p1[1], p1[0], p2[1], p2[0])
    return dist


def get_osm_map(lat,lon,zoom,items,line):
    extraMapOffset = 100
    x, y = smopy.deg2num(lat, lon, zoom)
    print("x,y is",x,y)
    x_coord, y_coord = smopy.get_tile_coords(lat, lon, zoom)
    x_coord, y_coord = 256 * (x_coord - int(x_coord)), 256 * (y_coord - int(y_coord)) ## x, y coords on a 768 x 768 map image
    print("xcvoord,ycoord is",x_coord,y_coord)
    #if x_coord < 128:
        #x -= 2
        #x_coord += 512
    #else:
    x -= 1
    x_coord += 256
    if y_coord < 128:
        y -= 2
        y_coord += 512
    else:
        y -= 1
        y_coord += 256
    full_img = Image.new("RGBA", (1280,1024), (0, 0, 0,0))
    img = smopy.fetch_map([x, y, x + 2, y + 3], zoom)
    print("size of initial img is",img.size)
    print("size of initial img is",img.size)
    #img.show()

    extra_img = smopy.fetch_map([x - 1, y, x - 1, y + 3], zoom)
    #extra_img.show()
    full_img.paste(extra_img, (0, 0))
    #full_img.show()
    extra_img = smopy.fetch_map([x + 3, y, x + 3, y + 3], zoom)
    #extra_img.show()
    full_img.paste(extra_img, (1024, 0))
    #full_img.show()
    full_img.paste(img, (256, 0))
    img = full_img
    #img.show()


    for item in items:
        print("drawing item",item)
        lat = item[1]
        lon= item[2]
        item_x,item_y = smopy.get_tile_coords(lat,lon,zoom)
        xoffset = (item_x - x) * 256
        yoffset = (item_y- y) * 256
        xoffset+=256 ### because we have added in an extra column of tiles at the start of the image
        #yoffset += 256
        print("offsets",xoffset,yoffset)
        marker = Image.open("NRTC/static/NRTC/" + item[0] + ".png")
        marker = marker.resize((40, 40), Image.ANTIALIAS)
        img.paste(marker, (int(xoffset)-20, int(yoffset)-40), mask=marker)
    coords = []
    lineImg = Image.new("RGBA", img.size, (0, 0, 0,0))
    for point in line:
        item_x, item_y = smopy.get_tile_coords(point[0], point[1], zoom)
        xoffset = (item_x - x) * 256
        xoffset += 256 ### because we have added in an extra column of tiles at the start of the image
        yoffset = (item_y - y) * 256
        coords.append((int(xoffset), int(yoffset)))
    draw = ImageDraw.Draw(lineImg)
    draw.line(coords, fill="black",width=9)
    img.paste(lineImg, (0, 0), mask=lineImg)



    ###
    ### we have added a column of tiles at the start of the image, which means that the x coord has increased by 256
    ###
    x_coord+=256
    left = x_coord - (768 / 2) - extraMapOffset
    top = y_coord - (768 / 2)

    img = img.crop((left, top, left + 768 + (2 * extraMapOffset), top + 768))
    trademark = Image.open("trademark.png")
    img.paste(trademark, (768 -172, 768-11))
    img = img.resize((453,350), Image.ANTIALIAS)
    return img


def fill_project_details(cpNo,fileName,zoom):
    proj = Project.objects.get(pk=cpNo)
    survey = proj.siteassessmentsurvey_set.values()[0]
    items = list(proj.siteassessmentsurvey_set.values_list("itemofinterest__itemType","itemofinterest__lat",
                                                           "itemofinterest__lon","itemofinterest__info",
                                                           "itemofinterest__permissions","itemofinterest__first"))
    items = [list(item) for item in items if item[0] != 5  and not item[0] is None]
    if hasattr(proj.siteassessmentsurvey_set.first(),"line"):
        line = proj.siteassessmentsurvey_set.first().line
        lineInfo = line.info
        line = [[line.lat1,line.lon1],[line.lat2,line.lon2]]

    else:
        line = []
        lineInfo = ""
    print("items are",items)
    for item in items:
        item[0] = itemTypes[item[0]]
        print("line is",line)
    dets = proj.__dict__
    existing_pdf = PyPDF2.PdfFileReader(open("Site Assessment Form.pdf", "rb"))
    output = PyPDF2.PdfFileWriter()
    ###
    ###   page 1
    ###

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold",10)
    y = 745


    can.drawString(180, y, str(cpNo))
    can.drawString(360, y, dets["roadNo"] + " " + dets["roadName"])
    y = y - 23
    if not survey["postcode"] is None:
        can.drawString(180, y, survey["postcode"])
    date = dets["scheduledDate"]
    try:
        date = datetime.datetime.strptime(date,"%Y-%m-%d")
    except Exception as e:
        ### TODO : do something about incorrect dateformat
        pass
    can.drawString(430, y, date.strftime("%d  %m"))

    y = y - 21
    date = dets["originalSurveyDate"]
    try:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    except Exception as e:
        ### TODO : do something about incorrect dateformat
        pass
    can.drawString(212, y, date.strftime("%d  %m"))
    can.drawString(450, y, str(dets["TFC"]))

    y = y - 21
    enumerators = tfcGrading[int(dets["TFC"])]
    can.drawString(225, y, str(enumerators[0]))
    can.drawString(480, y, str(enumerators[1]))


    y = y -448

    img = create_map_image_for_pdf(cpNo,items,line,zoom)
    img.convert("RGB").save("test.jpg")
    print("type of image is", type(img))
    print("size of image is",img.size)
    stringList = []
    firstParking = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(itemType=3, first=True)
    firstStandout = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(itemType=4, first=True)
    if len(firstParking) > 0:
        firstParking = firstParking[0]
        stringList.append(firstParking.info)
    else:
        firstParking = None
    print("first standout is",firstStandout)
    if len(firstStandout) > 0:
        firstStandout = firstStandout[0]
        stringList.append(firstStandout.info)
    else:
        firstStandout = None
    stringList.append(lineInfo)
    sizes = [stringWidth(text, "Helvetica", 8)  for text in stringList]
    print("sizes are",sizes)
    maxSize = int(max(sizes) + stringWidth("Standing Info: ", "Helvetica", 8))
    print("max size in pixels is",maxSize)
    blankBox = Image.new("RGB",(maxSize + 50,50),"white")
    #blankBox.show()
    img.paste(blankBox,(0,0))
    pdfImg = ImageReader(img)
    # img.save("overview.jpg")
    # img.show()

    print("y is", y)
    can.drawImage(pdfImg, 52, y+72, width=453, height=350)


    can.setFont("Helvetica", 8)
    can.setFillColorRGB(1, 0, 0)
    can.drawString(52, y + 412, "  Parking Info: ")
    can.drawString(52, y + 400, "Standing Info: " )
    can.drawString(52, y + 388, "         CP Info: ")
    can.setFillColorRGB(0, 0, 0)
    can.drawString(105,y+412,firstParking.info)
    if not firstStandout is None:
        can.drawString(105, y + 400, firstStandout[0].info)
    can.drawString(105, y + 388, lineInfo)
    print("aspersref is",survey["asPerSRef"])
    can.setFont("Helvetica-Bold", 10)
    if survey["asPerSRef"] == 0:
        can.drawString(435, y + 55, "X")
    else:
        can.drawString(480, y + 55, "X")

    if dets["iFlow"] == "1":
        can.drawString(190, y, "X")# str(dets["assignedEnumerators"]))
    else:
        can.drawString(300, y, "X")  # str(dets["assignedEnumerators"]))
    if survey["skewed"] == "1":
        can.drawString(468, y-1, "X")# str(dets["assignedEnumerators"]))
    y = y - 22
    can.drawString(148, y - 1, str(dets["speed"]))  # str(dets["assignedEnumerators"]))
    can.drawString(275, y - 1, str(dets["carriageways"]))
    can.drawString(390, y - 1, str(dets["lanes"]))

    y = y - 26
    if survey["streetLights"] == "1":
        can.drawString(245, y, "X")# str(dets["assignedEnumerators"]))
    else:
        can.drawString(290, y, "X")

    y = y - 27
    if survey["lessThan65"] == "1":
        can.drawString(398, y, "x")# str(dets["assignedEnumerators"]))
    elif survey["lessThan65"] == "2":
        can.drawString(450, y, "x")
    else:
        can.drawString(488, y, "x")

    y = y - 17
    if survey["lessThan65"] == "1":
        if survey["lowFlows"] == "1":
            can.drawString(398, y, "x")  # str(dets["assignedEnumerators"]))
        elif survey["lowFlows"] == "2":
            can.drawString(450, y, "x")
        elif survey["lowFlows"] == "3":
            can.drawString(488, y, "x")

    y = y - 16
    if survey["affectedByRoadworks"] == "1":
        can.drawString(398, y, "x")  # str(dets["assignedEnumerators"]))
    elif survey["affectedByRoadworks"] == "2":
        can.drawString(450, y, "x")
    else:
        can.drawString(488, y, "x")

    y = y - 16
    if survey["affectedByChangesToNetwork"] == "1":
        can.drawString(398, y, "x")  # str(dets["assignedEnumerators"]))
    elif survey["affectedByChangesToNetwork"] == "2":
        can.drawString(450, y, "x")
    else:
        can.drawString(488, y, "x")

    y = y - 36
    can.setFont("Helvetica", 8)
    if not survey["furtherDetails"] is None:
        can.drawString(65, y, survey["furtherDetails"])
    can.save()

    packet.seek(0)
    new_pdf = PyPDF2.PdfFileReader(packet)
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    ###
    ###   page 2
    ###

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 10)
    y = 660

    print("me is",survey["methodology"])
    if survey["methodology"] == "1":
        can.drawString(324, y , "x")
    elif survey["methodology"] == "2":
        can.drawString(324, y-9, "x")
    elif survey["methodology"] == "3":
        can.drawString(324, y-18, "x")
    elif survey["methodology"] == "4":
        print("woo")
        can.drawString(324, y-28, "x")

    y-=41
    can.drawString(270, y,str(survey["maxVehiclesOnSite"]))
    y -= 21
    can.setFont("Helvetica-Bold", 6)
    text = ""
    otherParkingText, permissionsText, otherPermissionsText, toiletLoc, toiletAccess, foodLoc, foodAccess,siteSpecificComments =format_complex_output(cpNo)
    can.drawString(235, y,  otherParkingText)
    y -= 27
    can.setFont("Helvetica-Bold", 10)
    if survey["highwayCode"] == 1:
        can.drawString(428, y, "X")
    y-=18
    if survey["distraction"] == 1:
        can.drawString(428, y, "X")
    elif survey["distraction"] == 2:
        can.drawString(476, y, "X")
    else:
        can.drawString(379, y, "X")

    y -= 21
    if survey["asbestos"] == 1:
        can.drawString(428, y, "X")
    elif survey["asbestos"] == 2:
        can.drawString(476, y, "X")
    y -= 37
    can.setFont("Helvetica-Bold", 6)


    can.drawString(55, y, permissionsText)
    y -= 29
    can.drawString(55, y, otherPermissionsText)

    #info = API.get_useful_info(cpNo)

    y-=47
    can.drawString(138, y,toiletLoc)
    can.drawString(332, y,toiletAccess)
    y -= 18
    can.drawString(138, y, "mobile")
    can.drawString(332, y,"N/A")
    y -= 18
    can.drawString(138, y,foodLoc)
    can.drawString(332, y,foodAccess)



    hospitals = OtherPlaces.objects.filter(itemType=6).values_list("id","lat","lon")
    centre = convert_from_1936_to_4326((proj.sRefE,proj.sRefN))
    hospital = sorted([[h[0],get_dist(centre,[h[1],h[2]])] for h in hospitals],key=lambda x:x[1])[0]
    hospital = OtherPlaces.objects.get(id=hospital[0])
    y -= 17
    can.drawString(238, y, hospital.name )
    can.drawString(450, y,hospital.postcode)

    y -= 38
    for item in siteSpecificComments:
        can.drawString(55, y, item)
        y -= 8
    signatureFile = survey["signature"]
    if os.path.exists(signatureFile):
        print("signature file is",signatureFile)
        img = Image.open(signatureFile)
        pdfImg = ImageReader(img)
        # img.save("overview.jpg")
        # img.show()

        print("y is", y)
        can.drawImage(pdfImg, 200, y -236, width=90, height=30,mask=[255,255,255,255,255,255])
    can.setFont("Helvetica-Bold", 9)
    d = datetime.datetime.now().date()
    can.drawString(420, y -230, str(d.day))
    can.drawString(446, y - 230, str(d.month))
    can.save()
    #packet.seek(0)
    #new_pdf = PyPDF2.PdfFileReader(packet)
    # read your existing PDF

    # add the "watermark" (which is the new pdf) on the existing page
    packet.seek(0)
    new_pdf = PyPDF2.PdfFileReader(packet)
    page = existing_pdf.getPage(1)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    # finally, write "output" to a real file
    outputStream = open(fileName, "wb")
    output.write(outputStream)
    outputStream.close()


def format_complex_output(cpNo):
    siteSpecificComments = []  ### this goes in the CP specific comments box, so any extra info gets tacked on here
    otherParkingText = ""
    permissionsText = ""
    otherPermissionsText = ""
    toiletLoc = ""
    toiletAccess = ""
    foodLoc = ""
    foodAccess = ""
    firstParking = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(itemType=3,first=True)
    firstStandout = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(itemType=4,first=True)
    if len(firstParking)> 0:
        firstParking = firstParking[0]
    else:
        firstParking = None
    if len(firstStandout)> 0:
        firstStandout = firstStandout[0]
    else:
        firstStandout = None
    otherParking = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(itemType=3, first=False)

    strSize = 0
    for i, p in enumerate(otherParking.values("info", "permissions")):
        # strSize = stringWidth(p["info"] + " - " + p["permissions"], "Helvetica", 6)
        if strSize + stringWidth(p["info"] + " - " + p["permissions"], "Helvetica", 6) < 400:
            otherParkingText += p["info"] + " - " + p["permissions"]
        else:
            siteSpecificComments.append("Alt Parking Info " + str(i + 1) + "): " + p["info"] + " - " + p["permissions"])
        strSize += stringWidth(p["info"] + " - " + p["permissions"], "Helvetica", 6)
        print("str size is now", strSize)
    print("otherparking is", otherParking)

    school = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(itemType=2)
    text = ""
    strSize = 0
    for i in range(len(school)):
        if strSize + stringWidth(school[i].info + " - School and Police informed. ", "Helvetica", 6)< 400:
            permissionsText += school[i].info + " - School and Police informed. "
            strSize = stringWidth(permissionsText, "Helvetica", 6)
            print("size after",i,strSize)
        else:
            siteSpecificComments.append(school[0].info + " - School and Police informed. ")
    print("size of permissions text is",strSize)
    if not firstParking is None and not firstParking.permissions is None and firstParking.permissions != "":
        if strSize  + stringWidth("Parking : " + firstParking.permissions, "Helvetica", 6) < 400:
            permissionsText += "Parking : " + firstParking.permissions
        else:
            siteSpecificComments.append("Primary Parking Permissions: " + firstParking.permissions)
    strSize = stringWidth(permissionsText, "Helvetica", 6)
    if not firstStandout is None and not firstStandout.permissions is None and firstStandout.permissions != "":
        if strSize  + stringWidth(" Standout : " + firstStandout.permissions, "Helvetica", 6) < 400:
            permissionsText += " Standout : " + firstStandout.permissions
        else:
            siteSpecificComments.append("Primary Standout Permissions: " + firstStandout.permissions)


    toilet = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(itemType=0, first=True)
    if len(toilet) > 0:
        if toilet[0].permissions != "" and not toilet[0].permissions is None:
            otherPermissionsText = "Toilet : " + toilet[0].permissions
        toiletLoc = toilet[0].info
        toiletAccess = toilet[0].accessMethod
    otherToilets = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(itemType=0, first=False)
    for i,p in enumerate(otherToilets.values("info","permissions")):
        siteSpecificComments.append(
            "Alt Toilets :" + str(i + 1) + "): " + p["info"] + " - " + p["permissions"])

    food = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(itemType=1,
                                                                                                            first=True)
    if len(food) > 0:
        foodLoc = food[0].info
        foodAccess = food[0].accessMethod
    otherFood = SiteAssessmentSurvey.objects.filter(project__countPointCode=cpNo)[0].itemofinterest_set.filter(
        itemType=1, first=False)
    for i, p in enumerate(otherFood.values("info")):
        siteSpecificComments.append(
            "Alt Refreshments :" + str(i + 1) + "): " + p["info"] )

    return [otherParkingText,permissionsText,otherPermissionsText,toiletLoc,toiletAccess,foodLoc,foodAccess,siteSpecificComments]


def create_map_image_for_pdf(cpNo,items,line,zoom):
    survey = SiteAssessmentSurvey.objects.get(project_id=cpNo)
    centre = convert_from_1936_to_4326((survey.project.sRefE, survey.project.sRefN))
    print("centre is",centre)
    img = get_osm_map(centre[0],centre[1],zoom,items,line)
    return img


#########################################################################
#
# API Functions for serving data to the nutshell app
#
#########################################################################


def get_count_point_data(request,projectNo):
    print("recieved",projectNo)
    if projectNo == "" or projectNo is None:
        raise Http404
    if Project.objects.filter(countPointCode = projectNo).exists():
        dict = Project.objects.filter(countPointCode = projectNo).values()[0]
        headers = ["roadName","scheduledDate","TFC","originalSurveyDate","roadNo","sRefE","sRefN","CP Code","postcode","minEnumerators","assignedEnumerators"]
        dict = {k:v for k,v in dict.items() if k in headers}
        #dict["asPerSRef"] = str(dict["asPerSRef"])
        print("sending back",dict)
        return JsonResponse(dict)
    else:
        raise Http404


@csrf_exempt
def get_survey_methodology(request,projectNo):
    print("recieved request for survey methodology", projectNo)
    if Project.objects.filter(countPointCode = projectNo).exists():
        dict = Project.objects.filter(countPointCode = projectNo).values()[0]
        headers = ["methodology","maxVehiclesOnSite","otherParking","highwayCode","distraction",
                   "asbestos","permissions","amenities"]
        dict = {k:v for k,v in dict.items() if k in headers}
        print("sending back", dict)
        return JsonResponse({"data":dict})
    else:
        raise Http404

@csrf_exempt
def get_useful_info(request,projectNo):
    print("recieved request for useful info", projectNo)
    if Project.objects.filter(countPointCode = projectNo).exists():
        dict = Project.objects.filter(countPointCode = projectNo).values()[0]
        print("dict is",dict)
        headers = ["siteSpecificComments","toilets","toiletsAccess","toiletsPostcode",
                   "telephone","telephoneAccess","telephonePostcode",
                   "refreshments","refreshmentsAccess","refreshmentsPostcode"]
        dict = {k:v for k,v in dict.items() if k in headers}
        #dict = {key: str(val) for key, val in dict.items()}
        # dict["lessThan65"] = "Yes"
        print("sending back", dict)
        return JsonResponse(dict)
    else:
        raise Http404

@csrf_exempt
def save_network_info(request):
    print("recived network info data!!!!")
    if request.method == "POST":
        data =request.POST
        print("received data",data,type(data))
        CPNo = request.session["CPNo"]
        print("CPno is",CPNo)
        proj = Project.objects.get(pk=CPNo)
        survey = SiteAssessmentSurvey.objects.get(project=proj)
        headers = ("skewed","streetLights","lessThan65","lowFlow",
                   "affectedByRoadworks","affectedByChangesToNetwork",
                   "highwayCode","distraction","asbestos",
                   )
        for header in headers:
            setattr(survey,header,["Yes","No","Maybe"].index(data[header])+1)
        setattr(survey,"maxVehiclesOnSite",int(data["maxVehiclesOnSite"]))
        setattr(survey, "methodology", int(data["methodology"]))
        setattr(survey, "furtherDetails", data["furtherDetails"])
        survey.save()
        return HttpResponseRedirect("photo")

    raise Http404

@csrf_exempt
def save_project_data(request):
    print("recived network info data!!!!")
    if request.method == "POST":
        data =json.loads(request.body.decode())
        if "data" in data:
            data = data["data"]
        print("received data",data,type(data))
        if data != "null" and "CP Code" in data:
            projectNo = data["CP Code"]
            try:
                instance = Project.objects.get(countPointCode=projectNo)
            except instance.DoesNotExist:
                raise Http404
            for key,item in data.items():
                if not item is None and not item == "null" and item != '"null"' and not item == "nan":
                    setattr(instance,key,item)
                instance.save()
            return JsonResponse({"status": "success"})
    raise Http404



@csrf_exempt
def initialise_schedule_at_start_of_year(request):
    pass


@csrf_exempt
def update_schedule_from_client_file(request):
    print("received shcedule")
    print("post is",request.POST)
    print(request.FILES)
    if request.FILES:
        print(request.FILES)
        filename = "schedule.csv"
        file = request.FILES["upload_file"]
        with default_storage.open(filename, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        print("looking in",settings.STATIC_ROOT + filename)
        projectDf = load_schedule_from_excel(default_storage.path("schedule.csv"))
        print("no of projects in schedule",len(projectDf))
        projectList = projectDf.to_dict(orient="records")
        for project in projectList:
            project["roadType"] = ["Major", "Minor"].index(project["roadType"])
            CPCode = project["countPointCode"]
            try:
                instance = Project.objects.get(countPointCode=CPCode)
                #print("project", CPCode, "already exists,updating current object")
                for key,value in project.items():
                    print("setting",key,"to",value)
                    setattr(instance,key,value)
                instance.save()
            except django.core.exceptions.ObjectDoesNotExist as e:
                #print("creating new project", CPCode)
                instance = Project.objects.create(**project)

            if SiteAssessmentSurvey.objects.filter(project=instance).exists():
                #print("yes, found network info")
                survey  = SiteAssessmentSurvey.objects.get(project=instance)
                #print("survey for project",instance.countPointCode,"is",survey.id)
            else:
                #print("No, no network info present,creating object")
                siteAssessmentSurveyInstance = SiteAssessmentSurvey.objects.create(project=instance)
        return JsonResponse({"status": "success"})
    return HttpResponseRedirect("supervisorindex")


@csrf_exempt
def load_schedule_from_excel(fileName):
        df = pd.read_csv(fileName)
        df = df[df["Count Point Code"].notnull()]
        #df = df.astype(int, errors="ignore")

        df.columns = ['countPointCode', 'roadType', 'originalSurveyDate', 'scheduledDate',
                      'TFC', 'method', 'roadNo', 'roadManagement', 'LAName', 'DfTRegion',
                      'CPCode', 'region', 'roadName', 'sRefE', 'sRefN', 'sRefMap', 'aRefE',
                      'aRefN', 'aRefMap', 'bRefE', 'bRefN', 'bRefMap', 'aDesc', 'bDesc',"speed","iFlow","carriageways","lanes","iDir"]
        df["originalSurveyDate"] = pd.to_datetime(df["originalSurveyDate"])
        df["scheduledDate"] = pd.to_datetime(df["scheduledDate"])
        df[["roadName","iDir","aRefMap","bRefMap","sRefMap"]] = df[["roadName","iDir","aRefMap","bRefMap","sRefMap"]].fillna("")
        df[["speed", "iFlow", "carriageways", "lanes","sRefE","sRefN","aRefE","aRefN","bRefE","bRefN"]] = df[["speed", "iFlow", "carriageways", "lanes","sRefE","sRefN","aRefE","aRefN","bRefE","bRefN"]].fillna(0)
        return df


def saf(request):
    print("at index")
    surveys = SiteAssessmentSurvey.objects.all().values_list("project__countPointCode",flat=True)
    context = {"surveys":surveys}
    template = loader.get_template('NRTC/SAFindex.html')
    return HttpResponse(template.render(context, request))


def index(request):
    template = loader.get_template('NRTC/logonScreen.html')
    return HttpResponse(template.render({}, request))


def view_choices(request):
    data = request.POST
    print(data["username"],data["password"])
    template = loader.get_template('NRTC/choices.html')
    return HttpResponse(template.render({}, request))


def get_map(request):
    print("here")
    print("data is",request.POST)
    if request.POST:
        CPNo = request.POST["CPNo"]
    else:
        CPNo = request.session["CPNo"]
    if CPNo == "-------":
        return HttpResponseRedirect("saf")

    try:
        int(CPNo)
    except ValueError as e:
        return HttpResponseRedirect("saf")

    request.session["CPNo"] = CPNo
    template = loader.get_template('NRTC/map.html')
    proj = Project.objects.filter(pk=CPNo)

    proj = list(proj.values_list("countPointCode","roadType","scheduledDate","TFC","roadNo","roadName","LAName","DfTRegion","CPCode","aDesc","bDesc","speed","iFlow","carriageways","lanes","iDir")[0])
    proj[1] = ["Major","Minor"][proj[1]]
    headers = ["CP No","Road Type","Scheduled Date","TFC","Road No","Road Name","LA Name","DfT Region","CP Code","A Desc","B Desc","Speed","iFlow","Carriageways","Lanes","iDir"]
    info = list(zip(headers,proj))
    print(proj)

    context = {
        "info":info
    }
    return HttpResponse(template.render(context, request))

####
###
### this is different to the get_network_info which was for the nutshell app
###
###

def get_networkInfo(request):
    CPNo = request.session["CPNo"]
    proj = Project.objects.get(pk=CPNo)
    survey = SiteAssessmentSurvey.objects.filter(project=proj).values("skewed","streetLights","lessThan65","lowFlow",
                                                                   "affectedByRoadworks","affectedByChangesToNetwork",
                                                                   "highwayCode","distraction","asbestos","methodology",
                                                                   "maxVehiclesOnSite","furtherDetails")[0]
    info = [["Skewed?","skewed",["Yes","No"],survey["skewed"]],["Street Lights?","streetLights",["Yes","No"],survey["streetLights"]],
            [" Less Than 65 Vehicles?","lessThan65",["Yes","No","Maybe"],survey["lessThan65"]],["Low Flow Site?","lowFlow",["Yes","No","Maybe"],survey["lowFlow"]],
             ["Traffic affected by roadworks/events","affectedByRoadworks", ["Yes", "No", "Maybe"],survey["affectedByRoadworks"]],
            ["Traffic affected changes to road network?","affectedByChangesToNetwork",["Yes","No","Maybe"],survey["affectedByChangesToNetwork"]]
            ,["Location Adheres to Highway Code","highwayCode",["Yes","No"],survey["highwayCode"]]
        , ["Location potential distraction for motorists?","distraction", ["Yes", "No"],survey["distraction"]]
        , ["Location is potential asbestos hazard?","asbestos", ["Yes", "No"],survey["asbestos"]]]
    template = loader.get_template('NRTC/networkInfo.html')
    context = {"info":info,"methodology":survey["methodology"],"furtherDetails":survey["furtherDetails"],"maxVehicles":survey["maxVehiclesOnSite"]}
    return HttpResponse(template.render(context, request))

def photo(request):
    template = loader.get_template('NRTC/photo.html')
    context = {}
    return HttpResponse(template.render(context, request))


def save_photo(request):
    CPNo = request.session["CPNo"]
    request.is_secure = True
    print("dealing with cpno", CPNo)
    saf = SiteAssessmentSurvey.objects.get(project__countPointCode=CPNo)
    print("data",request.POST)
    if request.method == 'POST':
        data = request.POST
        print("received ",data)
        if request.FILES:
            file_obj = request.FILES["imageFile"]
            print(settings.STATIC_ROOT)
            fileLoc = os.path.join(settings.MEDIA_ROOT, "photo for survey " + str(CPNo) + ".jpg")
            with default_storage.open(fileLoc, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            saf.sitePhoto = fileLoc
            saf.save()
            return HttpResponseRedirect("sign")


def sign_survey(request):
    data = request.POST
    print("received data",data)
    template = loader.get_template('NRTC/signature.html')
    context = {}
    return HttpResponse(template.render(context, request))


def finish_survey(request):
    CPNo = request.session["CPNo"]
    request.is_secure=True
    print("dealing with cpno",CPNo)
    saf = SiteAssessmentSurvey.objects.get(project__countPointCode=CPNo)
    if request.method == 'POST':
        data = request.POST
        print("received ",data)

        image_path = s2if(data["output"],os.path.join(settings.MEDIA_ROOT, "signature for survey " + str(CPNo) + ".jpg"),pincolor=(0,0,0))
        saf.signature = image_path
        saf.save()
    template = loader.get_template('NRTC/finish.html')
    context = {}
    return HttpResponse(template.render(context, request))

@ensure_csrf_cookie
def home_safe(request):
    request_csrf_token = request.META.get(settings.CSRF_HEADER_NAME, '')
    print(request_csrf_token)
    template = loader.get_template('NRTC/homeSafe.html')
    context = {}
    return HttpResponse(template.render(context, request))


def mark_home_safe(request):
    print("marking as home safe")
    return JsonResponse({"status":"success"})



#########################################################################
#
# functions for the supervisor app
#
#########################################################################



@csrf_exempt
def save_items_of_interest(request):
    CPNo = request.session["CPNo"]
    print("in save items,received cp no ", CPNo)
    survey = SiteAssessmentSurvey.objects.get(project_id=CPNo)

    data = json.loads(request.body.decode())
    print("received data",data.keys())

    if hasattr(survey,"line"):
        line = survey.line
    else:
        line = Line.objects.create(survey=survey)
    lineData =data["lineData"]
    line.lat1 = lineData[0]["lat"]
    line.lon1 = lineData[0]["lng"]
    line.lat2 = lineData[1]["lat"]
    line.lon2 = lineData[1]["lng"]
    line.info = data["lineInfo"]
    line.save()
    asPerSRef = data["sRef"]
    asPerSRef = ["Yes","No"].index(asPerSRef)
    survey.asPerSRef = asPerSRef
    survey.save()
    for item in data["markers"]:
        print("looking at item",item)
        if item[4] != "roadworks" and item[4] != "plannedroadworks":
            print(item[1],type(item[1]),item[1]["lat"])
            latitude = item[1]["lat"]
            longitude = item[1]["lng"]
            if item[4] == "Deleted":
                try:
                    ItemOfInterest.objects.filter(pk=int(item[0])).delete()
                    print("deleted item of interest",item[0])
                except Exception as e:
                    print("tried to delete item of interest",item[0]," got error",e)
            else:
                if not item[0] is None:
                    currentItem = ItemOfInterest.objects.get(pk=int(item[0]))
                else:
                    currentItem = ItemOfInterest.objects.create(survey=survey,lat=latitude,lon=longitude)
                currentItem.lat = item[1]["lat"]
                currentItem.lon = item[1]["lng"]
                currentItem.info = item[2]
                currentItem.permissions = item[3]
                currentItem.first=item[5]
                print("looking for ",item[4])
                currentItem.itemType = itemTypes.index(item[4])
                if item[6] != "":
                    currentItem.accessMethod = item[6]
                currentItem.save()
    #result = get_items_of_interest(request)
    return JsonResponse({"success":"success"})


@csrf_exempt
def get_items_of_interest(request):
    if "CPNo" in request.session:
        CPNo = request.session["CPNo"]
    else:
        CPNo = 653# request.session["CPNo"]
    print("received cp no ",CPNo)
    survey = SiteAssessmentSurvey.objects.get(project_id=CPNo)
    items = list(survey.itemofinterest_set.values())

    #print("items are",items)
    for item in items:
        item["itemType"] = itemTypes[item["itemType"]]
    centre = convert_from_1936_to_4326((survey.project.sRefE,survey.project.sRefN))
    line = []
    if hasattr(survey,"line"):
        line={"coords":[{"lat":survey.line.lat1,"lng":survey.line.lon1},{"lat":survey.line.lat2,"lng":survey.line.lon2}],"info":survey.line.info}
    #print("centre is",centre)
    ###
    ### get roadworks info
    ###
    if "roadworks-search" in request.session:
        startDate= request.session["roadworks-search"]["start"]
        endDate = request.session["roadworks-search"]["end"]
        if startDate is None or startDate == "":
            startDate = datetime.datetime.now()
        else:
            startDate = datetime.datetime.strptime(startDate,"%Y-%m-%d")
        if endDate is None or endDate == "":
            endDate = (startDate + datetime.timedelta(days=14))
        else:
            endDate = datetime.datetime.strptime(endDate,"%Y-%m-%d")
    else:
        startDate = datetime.datetime.now()
        endDate = (startDate + datetime.timedelta(days=14))
    #if survey.project.DfTRegion == "Scotland":
        #roadworks = NRTC.trafficscotland.get_all_roadworks_for_lat_lon(centre,startDate,endDate)
    #else:
        #roadworks = NRTC.roadworks.get_all_roadworks_for_lat_lon(centre, startDate, endDate)
    #for item in roadworks:
        #item["project_id"] = CPNo
    otherPlaces = OtherPlaces.objects.all().values()
    otherPlaces = [{"lat": item["lat"], "info": item["name"], "permissions": "", "lon": item["lon"],"itemType": itemTypes[item["itemType"]], "id": item["id"]} for item in otherPlaces]


    #items+=roadworks
    items+=otherPlaces
    #print("sending items of interest",items)
    return JsonResponse({"items": items,"centre":centre,"lineData":line})


@csrf_exempt
def search_for_roadworks(request):
    print("searching for roadworks!!!")
    if request.is_ajax():
        print("ajax is",json.loads(request.body.decode()))
        data = json.loads(request.body.decode())
        print("data is",data)
        s = ""
        e  = ""
        for item in data["form"]:
            print(item)
            if item["name"] == "start":
                s = item["value"]
            if item["name"] == "end":
                e = item["value"]
        request.session["roadworks-search"] = {"start":s,"end":e}
        return HttpResponseRedirect("getItemsOfInterest")


def login_view(request):
    pass

@csrf_exempt
def get_projects_list(request):
    print("starting")
    projects = Project.objects.filter(siteassessmentsurvey__adminCheckedOff=False).values("countPointCode","CPCode","DfTRegion","roadNo","roadName","originalSurveyDate","scheduledDate")
    headers = [("CP Code","w1"),("DfT Region","w3"),("Road No","w3"),("Road Name","w3"),("Original Survey Date","w3"),("Scheduled Date","w3"),("","w1")]
    template = loader.get_template('NRTC/supervisorindex.html')
    context = {"headers": headers, "projects": projects}
    print("finished")
    return HttpResponse(template.render(context, request))

def update_projects_list(request):
    if request.is_ajax():
        print("ajax is",json.loads(request.body.decode()))
        data = json.loads(request.body.decode())
        print("data is",data)
        filters = data["filters"]
        args = []
        headers = ["countPointCode", "DfTRegion", "roadNo", "roadName", "originalSurveyDate", "scheduledDate", ""]
        for filter in filters:
            columnIndex = int(filter["column"]) - 1
            filter["column"] = headers[columnIndex]
        args = {filter["column"]:filter["value"] for filter in filters}
        #value = data["value"]
        #args = {column:value}
        print("args are",args)
        projects = list(Project.objects.filter(**args).values_list("CPCode","DfTRegion","roadNo","roadName","originalSurveyDate","scheduledDate","countPointCode"))
        return JsonResponse({"data":projects})


def view_project(request,projectNo):
    print("project no is", projectNo)
    request.session["CPNo"] = projectNo
    proj = get_object_or_404(Project, pk=projectNo)
    request.session["projectNo"] = projectNo
    request.session["stage"] = 1
    exclude = ["sRefE","sRefN","sRefMap","aRefE","aRefN","aRefMap","bRefE","bRefN","bRefMap"]
    headers = Project._meta.get_fields()
    data = [[h.verbose_name,getattr(proj,h.name)] for h in headers if hasattr(h,"verbose_name") and not h.name in exclude]
    if data[1][1] in [0, 1]:
        data[1][1] = ["Major", "Minor"][data[1][1]]
    else:
        data[1][1] = ""

    survey = SiteAssessmentSurvey.objects.get(project_id=projectNo)
    exclude = ["asPerSRef","project","id"]
    attrList = ("skewed", "streetLights", "lessThan65", "lowFlow",
                "affectedByRoadworks", "affectedByChangesToNetwork",
                "highwayCode", "distraction", "asbestos",
                )
    surveyData = SiteAssessmentSurvey._meta.get_fields()
    headers = [h.verbose_name for h in surveyData if hasattr(h,"verbose_name") and not h.name in exclude]
    fields = [h.name for h in surveyData if hasattr(h,"verbose_name") and not h.name in exclude]
    vals = [["","Yes","No","Maybe"][getattr(survey,f)] if f in attrList and not getattr(survey,f) is None else getattr(survey,f) for f in fields]
    surveyData  = list(zip(headers,vals))
    items = list(survey.itemofinterest_set.values())
    items = [[itemTypes[item["itemType"]],item["info"],item["permissions"]] for item in items]
    context = {"project": data, "projectNo": projectNo,"action":"/nrtc/saveAdminChangesToProject","items":items,"surveyData":surveyData}
    if hasattr(survey,"line"):
        items.append(["line",survey.line.info])
    asPerSref = survey.asPerSRef
    if not asPerSref is None:
        asPerSref = ["green-tick.png", "cross.jpg"][survey.asPerSRef]
        context["asPersRef"] = asPerSref
    template = loader.get_template('NRTC/displayProject.html')
    return HttpResponse(template.render(context, request))


@csrf_exempt
def download_pdf(request):
    print("WOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
    data = request.POST
    print("data is",data)
    zoom = int(data["zoom-level"])
    if zoom > 19:
        zoom = 19
    projectNo=request.session["CPNo"]
    print("projectno is",projectNo)
    proj = get_object_or_404(Project, pk=projectNo)
    fileName = proj.CPCode + " assessment.pdf"
    fill_project_details(projectNo,fileName,zoom)
    with open(fileName, 'rb') as fh:
        response = HttpResponse(fh, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=' + fileName
        return response


def search_for_project(request):
    if request.method == 'POST':
        projectNo = request.POST["projectNo"]
        print("project no is",projectNo)
        try:
            projectNo = int(projectNo)
        except ValueError as e:
            return HttpResponseRedirect("projectsList")
        proj = get_object_or_404(Project,pk=projectNo)
        request.session["projectNo"] = projectNo
        request.session["stage"] = 1
        form = []#ProjectForm(instance=proj)
        context = {"project": form,"projectNo":projectNo,"action":"/nrtc/saveAdminChangesToProject"}
        template = loader.get_template('displayProject.html')
        return HttpResponse(template.render(context, request))

@csrf_exempt
def get_project_map(request):
    print("getting project map")
    projects = Project.objects.all()[:10]
    exclude = ["sRefE", "sRefN", "sRefMap", "aRefE", "aRefN", "aRefMap", "bRefE", "bRefN", "bRefMap"]
    headers = Project._meta.get_fields()
    data = []
    for proj in projects:
        details = [[h.verbose_name, getattr(proj, h.name)] for h in headers if hasattr(h, "verbose_name") and not h.name in exclude]
        print("road type",details[1][1],type(details[1][1]))
        if details[1][1] in [0, 1]:
            print("road type", details[1][1], type(details[1][1]))
            index = details[1][1]
            print("index is",index,)
            details[1][1] = ["Major", "Minor"][index]
        else:
            details[1][1] = ""
        centre = convert_from_1936_to_4326((proj.sRefE, proj.sRefN))
        details.insert(0, centre)
        data.append(details)
    print("no of projects", len(data))
    return JsonResponse({"data": data})


def view_all_projects(request):
    print("getting html for project map")
    context ={}
    template = loader.get_template('NRTC/projectMap.html')
    return HttpResponse(template.render(context, request))

def get_column_values(request):
    if request.is_ajax():
        data = json.loads(request.body.decode())
        print("data is",data)
        headers = ["countPointCode","DfTRegion","roadNo","roadName","originalSurveyDate","scheduledDate",""]
        filters = data["filters"]
        for filter in filters:
            columnIndex = int(filter["column"]) - 1
            filter["column"] = headers[columnIndex]
        args = {filter["column"]: filter["value"] for filter in filters}
        print("args are",args)
        columnIndex = int(data["column"])-1
        column = headers[columnIndex]
        result = list(Project.objects.filter(**args).values_list(column,flat=True).distinct().order_by(column))
        print("result is",result[:10])
        data = {}
        data['columnValues'] = []
        for index,item in enumerate(result):
            data['columnValues'].append('''<li onclick='filterBy(\"''' + str(columnIndex + 1) + '''\", \"''' + str(item) + '''\")'>''' + str(item) + '''</li>''')
        data["columnValues"] = "".join(data["columnValues"])
        return JsonResponse({"data":data})
    raise Http404

def filter_by(request):
    return Http404