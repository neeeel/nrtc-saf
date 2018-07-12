import requests

def get_postcode(lat,lon):
    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + str(lat) + "," + str(lon) + "&sensor=true_or_false&key=AIzaSyDRVvMxvveTE7ladKBhUnptw9-lOoHMAAU"
    print(url)
    r = requests.get(url)
    print(r.json())
    result = r.json()
    for item in result["results"][0]["address_components"]:
        # print(item["types"][0])
        if item["types"][0] == "route":
            road = item["long_name"]
        if item["types"][0] == "postal_code":
            postcode = item["long_name"]

            return postcode
    return ""


print(get_road_name(55.929557, -3.506674))