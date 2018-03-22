from django.forms import ModelForm,ChoiceField,HiddenInput,ModelChoiceField
from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import Project,NetworkInfo


class ProjectForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        #self.fields["projectDate"].input_formats = ["%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y"]
        #self.fields["uploadedData"].widget = forms.FileInput

    class Meta:

        model = Project
        fields = ["CPCode","roadNo","roadName","postcode","originalSurveyDate","scheduledDate","TFC","sRefE","sRefN","minEnumerators","assignedEnumerators"]


class NetworkInfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NetworkInfoForm, self).__init__(*args, **kwargs)
        #self.fields["projectDate"].input_formats = ["%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y"]
        #self.fields["uploadedData"].widget = forms.FileInput
        print("lessthan65 is",self.instance.lessThan65,type(self.instance.lessThan65))
        if self.instance.lessThan65 != "1" and self.instance.lessThan65 != 1:
            del self.fields["lowFlow"]

    class Meta:

        model = NetworkInfo

        fields = ["lanes","carriageways","speed","iFlow","skewed","streetLights","affectedByRoadworks","affectedByChangesToNetwork","lessThan65","lowFlow","furtherDetails"]

class SurveyMethodologyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyMethodologyForm, self).__init__(*args, **kwargs)
        #self.fields["projectDate"].input_formats = ["%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y"]
        #self.fields["uploadedData"].widget = forms.FileInput

    class Meta:

        model = Project
        fields = ["methodology","maxVehiclesOnSite","otherParking","highwayCode","distraction",
                   "asbestos","permissions","amenities"]

class UsefulInfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(UsefulInfoForm, self).__init__(*args, **kwargs)
        #self.fields["projectDate"].input_formats = ["%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y"]
        #self.fields["uploadedData"].widget = forms.FileInput

    class Meta:

        model = Project
        fields = ["siteSpecificComments","toilets","toiletsAccess","toiletsPostcode",
                   "telephone","telephoneAccess","telephonePostcode",
                   "refreshments","refreshmentsAccess","refreshmentsPostcode"]