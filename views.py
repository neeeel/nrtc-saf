from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,JsonResponse,Http404,HttpResponseRedirect
import json
from .models import Project,NetworkInfo
from django.views.decorators.csrf import csrf_exempt
import django.core.exceptions
from django.core.files.storage import default_storage
import pandas as pd
from django.template import loader, Context
from NRTC.forms import ProjectForm,NetworkInfoForm,SurveyMethodologyForm,UsefulInfoForm


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. Nothing to see here!")

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
def get_network_info(request,projectNo):
    print("recieved request for network info", projectNo)
    if NetworkInfo.objects.filter(project=projectNo).exists():
        dict = NetworkInfo.objects.filter(project=projectNo).values()[0]
        dict = {key:str(val) for key,val in dict.items()}
        #dict["lessThan65"] = "Yes"
        print("sending back", dict)
        return JsonResponse({"data":dict})
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
        data =json.loads(request.body.decode())
        print("received data",data,type(data))
        if data != "null" and "CP Code" in data:
            projectNo = data["CP Code"]
            try:
                instance = Project.objects.get(countPointCode=projectNo)
            except  django.core.exceptions.ObjectDoesNotExist as e:
                raise Http404
            networkInfo = instance.networkinfo
            for key,item in data.items():
                if not item is None and not item == "null" and item != '"null"' and not item == "nan":
                    setattr(networkInfo,key,item)
            networkInfo.save()
            return JsonResponse({"status": "success"})
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
def save_count_point_info(request):
    if request.method == "POST":
        data =json.loads(request.body.decode())
        print("received data",data)
        if "asPerSRef" in data:
            del data["asPerSRef"]
        if data != "null" and "CP Code" in data:
            projectNo = data["CP Code"]
            print("projectno is",projectNo)
            try:
                instance = Project.objects.get(countPointCode=projectNo)
            except instance.DoesNotExist:
                raise Http404
            for key,item in data.items():
                if not item is None and not item == "null" and not item == "nan":
                    setattr(instance,key,item)
            instance.save()
            if NetworkInfo.objects.filter(project=instance).exists():
                print("yes, found network info")
                print(instance.networkinfo)
            else:
                print("No, no network info present,creating object")
                NetworkInfo.objects.create(project=instance)
            return JsonResponse({"status": "success"})
    raise Http404

@csrf_exempt
def load_schedule_from_excel(request):
    if request.FILES:
        print(request.FILES)
        filename = "schedule.csv"
        file = request.FILES["upload_file"]
        with default_storage.open(filename, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        df = pd.read_csv("schedule.csv")
        df = df[df["Count Point Code"].notnull()]
        df = df.astype(int, errors="ignore")
        networkInfo = df[[i for index, i in enumerate(list(df.columns)) if index in [0, 24, 25, 26, 27, 28]]]
        networkInfo.columns = ["countPointCode", "speed", "iFlow", "carriageways", "lanes", "iDir"]
        print(networkInfo[networkInfo["countPointCode"] == 1].to_dict())
        df.drop(df.columns[[-1, -2, -3, -4, -5]], axis=1, inplace=True)
        df.columns = ['countPointCode', 'roadType', 'originalSurveyDate', 'scheduledDate',
                      'TFC', 'method', 'roadNo', 'roadManagement', 'LAName', 'DfTRegion',
                      'CPCode', 'region', 'roadName', 'sRefE', 'sRefN', 'sRefMap', 'aRefE',
                      'aRefN', 'aRefMap', 'bRefE', 'bRefN', 'bRefMap', 'aDesc', 'bDesc']

        projectDf = df[['countPointCode', 'roadType', 'originalSurveyDate', 'scheduledDate',
                        'TFC', 'method', 'roadNo', 'roadManagement', 'LAName', 'DfTRegion',
                        'CPCode', 'region', 'roadName', 'sRefE', 'sRefN', 'sRefMap', 'aRefE',
                        'aRefN', 'aRefMap', 'bRefE', 'bRefN', 'bRefMap', 'aDesc', 'bDesc']]
        projectDf["originalSurveyDate"] = pd.to_datetime(projectDf["originalSurveyDate"])
        projectDf["scheduledDate"] = pd.to_datetime(projectDf["scheduledDate"])
        projectList = projectDf.to_dict(orient="records")
        for survey in projectList[:100]:
            survey["roadType"] = ["Major", "Minor"].index(survey["roadType"])
            CPCode = survey["countPointCode"]
            try:
                instance = Project.objects.get(countPointCode=CPCode)
                print("project",CPCode,"already exists")
            except django.core.exceptions.ObjectDoesNotExist as e:
                print("creating new project",CPCode)
                instance = Project.objects.create(**survey)

            if NetworkInfo.objects.filter(project=instance).exists():
                print("yes, found network info")
                print(instance.networkinfo)
            else:
                print("No, no network info present,creating object")
                networkInstance = NetworkInfo.objects.create(project=instance)
                networkDict = networkInfo[networkInfo["countPointCode"] == CPCode].to_dict()
                for key, item in networkDict.items():
                    if not item is None and not item == "null" and not item == "nan":
                        setattr(networkInstance, key, item)
                print(networkInstance.speed)

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failure"})

#########################################################################
#
# functions for the supervisor app
#
#########################################################################

def login_view(request):
    pass

def get_projects_list(request):
    projects = Project.objects.filter(adminCheckedOff=False).values("countPointCode","CPCode","DfTRegion","roadNo","roadName","originalSurveyDate","scheduledDate")
    headers = ["","CPCode","DfTRegion","roadNo","roadName","originalSurveyDate","scheduledDate"]
    template = loader.get_template('projects.html')
    context = {"headers": headers, "projects": projects}
    return HttpResponse(template.render(context, request))

def view_project(request,projectNo):
    print("project no is", projectNo)
    proj = get_object_or_404(Project, pk=projectNo)
    request.session["projectNo"] = projectNo
    request.session["stage"] = 1
    form = ProjectForm(instance=proj)
    context = {"project": form, "projectNo": projectNo,"action":"/nrtc/saveAdminChangesToProject"}
    template = loader.get_template('displayProject.html')
    return HttpResponse(template.render(context, request))

def save_admin_changes_to_project_data(request):
    if request.method == 'POST':
        projectNo = request.session["projectNo"]
        print("project no is", projectNo)
        proj = get_object_or_404(Project, pk=projectNo)
        if request.session["stage"] == 1:
            networkInfo = proj.networkinfo
            form = NetworkInfoForm(instance=networkInfo)
            request.session["stage"] = 2
        elif request.session["stage"] == 2:
            form = SurveyMethodologyForm(instance=proj)
            request.session["stage"] = 3
        elif request.session["stage"] == 3:
            form = UsefulInfoForm(instance=proj)
            request.session["stage"] = 4
        elif request.session["stage"] == 4:
            return HttpResponse("Finished")
        context = {"project": form, "projectNo": projectNo,"action":"/nrtc/saveAdminChangesToProject"}
        template = loader.get_template('displayProject.html')
        return HttpResponse(template.render(context, request))





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
        form = ProjectForm(instance=proj)
        context = {"project": form,"projectNo":projectNo,"action":"/nrtc/saveAdminChangesToProject"}
        template = loader.get_template('displayProject.html')
        return HttpResponse(template.render(context, request))

