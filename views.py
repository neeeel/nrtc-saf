from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,Http404
import json
from .models import Project,NetworkInfo
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    print("recieved")
    return HttpResponse("Hello, world. You're at the polls index.")


def get_count_point_data(request,projectNo):
    print("recieved",projectNo)
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
def get_network_info(request,projectNo):
    print("recieved request for network info", projectNo)
    if NetworkInfo.objects.filter(project=projectNo).exists():
        dict = NetworkInfo.objects.filter(project=projectNo).values()[0]
        dict = {key:str(val) for key,val in dict.items()}
        #dict["lessThan65"] = "Yes"
        print("sending back", dict)
        return JsonResponse(dict)
    else:
        raise Http404

@csrf_exempt
def get_survey_methodology(request,projectNo):
    print("recieved request for survey methodology", projectNo)
    if Project.objects.filter(countPointCode = projectNo).exists():
        dict = Project.objects.filter(countPointCode = projectNo).values()[0]
        headers = ["siteSpecificComments","maxVehiclesOnSite","otherParking","highwayCode","distraction",
                   "asbestos","permissions","amenities"]
        dict = {k:v for k,v in dict.items() if k in headers}
        print("sending back", dict)
        return JsonResponse(dict)

@csrf_exempt
def get_useful_info(request,projectNo):
    print("recieved request for useful info", projectNo)
    if Project.objects.filter(countPointCode = projectNo).exists():
        dict = Project.objects.filter(countPointCode = projectNo).values()[0]
        print("dict is",dict)
        headers = ["toilets","toiletsAccess","toiletsPostcode",
                   "telephone","telephoneAccess","telephonePostcode",
                   "refreshments","refreshmentsAccess","refreshmentsPostcode"]
        dict = {k:v for k,v in dict.items() if k in headers}
        #dict = {key: str(val) for key, val in dict.items()}
        # dict["lessThan65"] = "Yes"
        print("sending back", dict)
        return JsonResponse(dict)


def update_count_point_data(request):
    settings = json.loads(request.body.decode())
    print("data is", settings)


@csrf_exempt
def get_stuff_back(request):
    print(request.session)
    settings = json.loads(request.body.decode())
    print("data is", settings)
    return JsonResponse({"road name": "wibble"})


@csrf_exempt
def save_network_info(request):
    print("recived network info dat!!!!")
    if request.method == "POST":
        data =json.loads(request.body.decode())
        print("received data",data,type(data))
        if data != "null":
            projectNo = data["CP Code"]
            instance = Project.objects.get(countPointCode=projectNo)
            networkInfo = instance.networkinfo
            for key,item in data.items():
                setattr(networkInfo,key,item)
            networkInfo.save()
    return JsonResponse({"road name": 111})

@csrf_exempt
def save_project_data(request):
    print("recived network info data!!!!")
    if request.method == "POST":
        data =json.loads(request.body.decode())
        print("received data",data,type(data))
        if data != "null":
            projectNo = data["CP Code"]
            instance = Project.objects.get(countPointCode=projectNo)
            for key,item in data.items():
                setattr(instance,key,item)
                instance.save()
    return JsonResponse({"road name": 111})




@csrf_exempt
def save_count_point_info(request):
    if request.method == "POST":
        data =json.loads(request.body.decode())
        print("received data",data)
        if "asPerSRef" in data:
            del data["asPerSRef"]
        projectNo = data["CP Code"]
        print("projectno is",projectNo)
        instance = Project.objects.get(countPointCode = projectNo)
        for key,item in data.items():
            setattr(instance,key,item)
        instance.save()
        if NetworkInfo.objects.filter(project=instance).exists():
            print("yes, found network info")
            print(instance.networkinfo)
        else:
            print("No, no network info present,creating object")
            NetworkInfo.objects.create(project=instance)
    return JsonResponse({"road name": 111})

def load_schedule_from_excel(request):
    if request.FILES:
        pass