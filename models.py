from django.db import models
from django.db.models import CASCADE
# Create your models here.

yesNoChoices = [("1","Yes"),("2","No")]
yesNoMaybeChoices = [("1","Yes"),("2","No"),("3","Maybe")]
methodologyChoices = [("1","Within Vehicles Parked Off Street"),
                      ("2","Within Vehicles Parked On Street"),
                      ("3","Within Vehicles Parked On Bridge/Hard Standing"),
                      ("4","Count Performed Outside of Vehicles")]

class Project(models.Model):
    countPointCode = models.IntegerField(primary_key=True)
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
    postcode = models.CharField("Postcode",max_length=20,blank=True,null=True)
    minEnumerators = models.IntegerField("Min Enumerators",blank=True,null=True)
    assignedEnumerators = models.IntegerField("Assigned Enumerators",blank=True,null=True)
    asPerSRef = models.IntegerField("As per scheduled SRef?",blank=True,null=True)

    methodology = models.CharField("Survey Methodology",blank=True,default="1", max_length=256,choices=methodologyChoices)
    maxVehiclesOnSite = models.IntegerField("Max Vehicles Parked at Site",blank=True,null=True)
    otherParking = models.CharField("Other Parking", blank=True, null=True, max_length=256)
    highwayCode = models.IntegerField("Location adheres to highway code", blank=True, null=True,choices=[(0,"No"),(1,"Yes")])
    distraction = models.IntegerField("Possible Distraction to Motorists?", blank=True, null=True,choices=[(0,"No"),(1,"Yes")])
    asbestos = models.IntegerField("Possible Asbestos Hazard?", blank=True, null=True,choices=[(0,"No"),(1,"Yes")])
    permissions = models.CharField("Permissions (eg land owners,schools,police)", blank=True, null=True, max_length=256)
    amenities = models.CharField("Permissions for amenities other than supermarkets", blank=True, null=True, max_length=256)


    toilets = models.CharField("Location of Toilets",blank=True,null=True, max_length=256)
    toiletsAccess = models.CharField("Toilets Access Method",blank=True,null=True, max_length=256)
    toiletsPostcode = models.CharField("Toilets Postcode",blank=True,null=True, max_length=256)
    telephone = models.CharField("Location of Telephone", blank=True, null=True, max_length=256)
    telephoneAccess = models.CharField("Telephone Access Method", blank=True, null=True, max_length=256)
    telephonePostcode = models.CharField("Telephone Postcode", blank=True, null=True, max_length=256)
    refreshments = models.CharField("Location of Refreshments", blank=True, null=True, max_length=256)
    refreshmentsAccess = models.CharField("Refreshments Access Method", blank=True, null=True, max_length=256)
    refreshmentsPostcode = models.CharField("Refreshments Postcode", blank=True, null=True, max_length=256)
    siteSpecificComments = models.CharField("Site Specific Comments", blank=True, null=True, max_length=256)
    adminCheckedOff = models.BooleanField("Checked by Admin",default=False)


class NetworkInfo(models.Model):
    project = models.OneToOneField(Project,on_delete=CASCADE)
    speed = models.IntegerField("Speed Limit",default=60)
    iFlow = models.IntegerField("IFlow",default="1",choices=[("1","One Way"),("2","Two Way")])
    carriageways = models.IntegerField("Carriageways",default=1)
    lanes = models.IntegerField("Lanes",default=1)
    iDir = models.CharField("iDir", max_length=10,blank=True,null=True)
    streetLights = models.IntegerField("Street Lights",blank=True,null=True,choices=yesNoChoices)
    skewed = models.IntegerField("Skewed",blank=True,null=True,choices=yesNoChoices)
    lessThan65 = models.IntegerField("Less Than 65 Vehicles?",blank=True,null=True,choices=yesNoMaybeChoices)
    affectedByRoadworks = models.IntegerField("Traffic affected by roadwork events?",blank=True,null=True,choices=yesNoMaybeChoices)
    affectedByChangesToNetwork = models.IntegerField("Traffic affected by changes to road network/land use?",blank=True,null=True,choices=yesNoMaybeChoices)
    furtherDetails = models.TextField("Further Details",blank=True,null=True)
    lowFlow = models.IntegerField("Low Flow Site?",blank=True,null=True)



