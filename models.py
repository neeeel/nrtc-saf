from django.db import models
from django.db.models import CASCADE
# Create your models here.

yesNoChoices = [("1","Yes"),("2","No")]
yesNoMaybeChoices = [("1","Yes"),("2","No"),("3","Maybe")]
methodologyChoices = [("1","Within Vehicles Parked Off Street"),
                      ("2","Within Vehicles Parked On Street"),
                      ("3","Within Vehicles Parked On Bridge/Hard Standing"),
                      ("4","Count Performed Outside of Vehicles")]
itemOfInterestChoices = [(0,"Toilet"),(1,"food"),(2,"School"),(3,"parking"),(4,"standout"),(5,"warning"),(6,"hospital"),(7,"military")]

class Project(models.Model):
    countPointCode = models.IntegerField(primary_key=True,verbose_name="Count Point No")
    roadType = models.IntegerField("Road Type",choices = ((0,"Major"),(1,"Minor")),blank=True,null=True)
    originalSurveyDate = models.DateField("Pre Survey Visit Date",blank=True,null=True)
    scheduledDate = models.DateField("Scheduled Date")
    TFC= models.IntegerField("TFC")
    method = models.CharField("method", max_length=11)
    roadNo = models.CharField("road number", max_length=10,blank=True,null=True)
    roadManagement = models.CharField("Road Management", max_length=256)
    LAName = models.CharField("LA Name", max_length=256)
    DfTRegion = models.CharField("DfT Region", max_length=256)
    CPCode = models.CharField("CP Code", max_length=10)
    region = models.CharField("Country/Region", max_length=256)
    roadName = models.CharField("Road Name at CP", max_length=256,blank=True,null=True)
    sRefE = models.IntegerField("S Ref E")
    sRefN = models.IntegerField("S Ref N")
    sRefMap = models.CharField("S RefMap", max_length=256)
    aRefE = models.IntegerField("A Ref E")
    aRefN = models.IntegerField("A Ref E")
    aRefMap = models.CharField("A Ref Map", max_length=256)
    bRefE = models.IntegerField("B Ref E")
    bRefN = models.IntegerField("B Ref E")
    bRefMap = models.CharField("B Ref Map", max_length=256)
    aDesc = models.CharField("A Description", max_length=256)
    bDesc = models.CharField("B Description", max_length=256)
    speed = models.IntegerField("Speed Limit", default=60)
    iFlow = models.IntegerField("IFlow", default="1", choices=[("1", "One Way"), ("2", "Two Way")])
    carriageways = models.IntegerField("Carriageways", default=1)
    lanes = models.IntegerField("Lanes", default=1)
    iDir = models.CharField("iDir", max_length=10, blank=True, null=True)



class SiteAssessmentSurvey(models.Model):
    project = models.ForeignKey(Project, on_delete=CASCADE, verbose_name="Count Point Number")
    methodology = models.CharField("Methodology",blank=True,default="1", max_length=256,choices=methodologyChoices)
    maxVehiclesOnSite = models.IntegerField("Max Vehicles at Site",blank=True,null=True)
    otherParking = models.CharField("Other Parking", blank=True, null=True, max_length=256)
    highwayCode = models.IntegerField("adhere to HWay code", blank=True, null=True,choices=yesNoChoices)
    distraction = models.IntegerField("Possible Distraction?", blank=True, null=True,choices=yesNoChoices)
    asbestos = models.IntegerField("Asbestos Hazard?", blank=True, null=True,choices=yesNoChoices)
    adminCheckedOff = models.BooleanField("Checked by Admin", default=False)
    postcode = models.CharField("Postcode", max_length=20, blank=True, null=True)
    minEnumerators = models.IntegerField("Min Enums", blank=True, null=True)
    assignedEnumerators = models.IntegerField("Assigned Enums", blank=True, null=True)
    signature = models.ImageField("Signature", blank=True, null=True)
    sitePhoto = models.ImageField("photo", blank=True, null=True)

    ###
    ### network info
    ###

    streetLights = models.IntegerField("Street Lights",blank=True,null=True,choices=yesNoChoices)
    skewed = models.IntegerField("Skewed",blank=True,null=True,choices=yesNoChoices)
    lessThan65 = models.IntegerField("< 65 Vehicles?",blank=True,null=True,choices=yesNoMaybeChoices)
    affectedByRoadworks = models.IntegerField("Roadworks?",blank=True,null=True,choices=yesNoMaybeChoices)
    affectedByChangesToNetwork = models.IntegerField("Road Network?",blank=True,null=True,choices=yesNoMaybeChoices)
    furtherDetails = models.TextField("Further Details",blank=True,null=True,default="")
    lowFlow = models.IntegerField("Low Flow Site?",blank=True,null=True)
    asPerSRef = models.IntegerField("As per scheduled SRef?", blank=True, null=True)
    siteInfo = models.CharField("Site Info", max_length=1000, blank=True, null=True)


class ItemOfInterest(models.Model):
    survey = models.ForeignKey(SiteAssessmentSurvey,on_delete=CASCADE,verbose_name="Item of Interest")
    itemType = models.IntegerField("Location of Telephone",blank=True,null=True,choices=itemOfInterestChoices)
    lat = models.FloatField()
    lon = models.FloatField()
    info = models.CharField("Info", blank=True, null=True, max_length=256)
    permissions = models.CharField("Permissions", blank=True, null=True, max_length=256)
    postcode = models.CharField("Postcode", max_length=20, blank=True, null=True)
    first = models.BooleanField("first",default=False)
    accessMethod = models.CharField("Access Method", max_length=20, blank=True, null=True)

class OtherPlaces(models.Model):
    itemType = models.IntegerField("Place",blank=True,null=True,choices=itemOfInterestChoices)
    lat = models.FloatField()
    lon = models.FloatField()
    name = models.CharField("name", blank=True, null=True, max_length=256)
    postcode = models.CharField("Postcode", max_length=20, blank=True, null=True)

class Line(models.Model):
    survey = models.OneToOneField(SiteAssessmentSurvey,on_delete=CASCADE,verbose_name="Line Info")
    lat1 = models.FloatField(blank=True,null=True)
    lon1 = models.FloatField(blank=True,null=True)
    lat2 = models.FloatField(blank=True,null=True)
    lon2 = models.FloatField(blank=True,null=True)
    info = models.CharField("Info", blank=True, null=True, max_length=256)
