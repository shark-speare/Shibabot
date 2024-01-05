import requests

url = "https://opendata.cwa.gov.tw/linked/graphql"
key = "CWA-3FF8D5E8-035D-4F66-BD63-CFF6EDB21C2D"


payload = {
    "query": "query forecast { forecast { locations(locationName: \"苗栗縣\") { PoP12h { description, timePeriods { startTime, endTime, probabilityOfPrecipitation, measures } }, T { description, timePeriods { startTime, endTime, temperature, measures } }, MinT { description, timePeriods { startTime, endTime, temperature, measures } }, MaxT { description, timePeriods { startTime, endTime, temperature, measures } }, UVI { description, timePeriods { startTime, endTime, UVIndex, UVIDescription, measures } }, WeatherDescription { description timePeriods { startTime, endTime, weatherDescription, measures } }, Wx { description, timePeriods { startTime, endTime, weather, weatherIcon, measures } }, } } }",
    "variables": None
}
response = requests.post(url = url,params={"Authorization":key},json = payload)

print(response.json()["data"]["forecast"]["locations"][0]["PoP12h"]["timePeriods"][0]["probabilityOfPrecipitation"])