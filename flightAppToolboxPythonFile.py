# -*- coding: utf-8 -*-
import arcpy
import datetime
import requests

#icaoParam = ""
# keeps the ICAO code in there

res = requests.get("https://opensky-network.org/api/states/all?time=0&icao24=ad79eb,ad3c27,aae2f1,a6f581,a8aa77,a1fc3b,ad0e23,aa6bc0,a0a8df,a40027")
#provides three different flights based off of ICAO codes

data = res.json()

#for flight in data['states']:
#    print(flight)

#res.json returns a dictionary dictionary

#arcpy.management.Append()

#put data into feature class
fields = ['icao24',
          'callsign',
          'origin_country',
          'time_position',
          'last_contact',
          'lon',
          'lat',
          'altitude_baro',
          'on_ground_position',
          'velocity',
          'true_track',
          'vertical_rate',
          'sensors',
          'geo_altitude',
          'squawk',
          'spi',
          'position_source']

cursor = arcpy.da.InsertCursor('C:\\Users\\Micah D Johns\\Documents\\ArcGIS\\Projects\\FlightApp\\FlightApp.gdb\\FlightData', fields)

for flight in data['states']:
    cursor.insertRow(flight)
    arcpy.management.XYTableToPoint('FlightData', r"C:\Users\Micah D Johns\Documents\ArcGIS\Projects\FlightApp\FlightApp.gdb\FlightData_XYTableToPoint", "lon", "lat")
    print("flight position added")

arcpy.management.Append("FlightData_XYTableToPoint", "FlightDataPublished", "NO_TEST")
print("data published")

#gives coherent time to field based off of unix time
arcpy.management.ConvertTimeField('FlightDataPublished', 'time_position', 'unix_s', 'position_datetime', 'DATE')


#cleans out all the old data
arcpy.management.DeleteFeatures('FlightData_XYTableToPoint')
print("temp data deleted")

#calculate field for icao + callsign
arcpy.management.CalculateField("FlightDataPublished", "icao24Callsign", "!icao24! + !callsign!", "PYTHON3", '', "TEXT")

#creates copy feature class of flight data
arcpy.conversion.FeatureClassToFeatureClass("FlightDataPublished", r"C:\Users\Micah D Johns\Documents\ArcGIS\Projects\FlightApp\FlightApp.gdb", "UniqueFlightIDList")

#removes identical points, isolating only the unique flight IDs
arcpy.management.DeleteIdentical("UniqueFlightIDList", "icao24Callsign", None, 0)


UniqueFlightIdList = 'C:\\Users\\Micah D Johns\\Documents\\ArcGIS\\Projects\\FlightApp\\FlightApp.gdb\\UniqueFlightIDList'
queryFields = ['icao24Callsign']
uniqueListOfFlights = []
fields = ['icao24',
          'callsign',
          'origin_country',
          'time_position',
          'last_contact',
          'lon',
          'lat',
          'altitude_baro',
          'on_ground_position',
          'velocity',
          'true_track',
          'vertical_rate',
          'sensors',
          'geo_altitude',
          'squawk',
          'spi',
          'position_source',
          'icao24Callsign',
          'position_datetime']


burnerLayer = arcpy.da.InsertCursor('C:\\Users\\Micah D Johns\\Documents\\ArcGIS\\Projects\\FlightApp\\FlightApp.gdb\\BurnerLayerToCreateFlightPath', fields)
FlightDataPublished = 'C:\\Users\\Micah D Johns\\Documents\\ArcGIS\\Projects\\FlightApp\\FlightApp.gdb\\FlightDataPublished'

#gives you a unique list of flights to work off of
with arcpy.da.SearchCursor(UniqueFlightIdList, queryFields) as cursor:
    for i in cursor:
        uniqueListOfFlights.append(i[0])

print(uniqueListOfFlights)

#uniqueListOfFlights = []
matchedFlightPoints = []
for value in uniqueListOfFlights:
    expressionText = " icao24Callsign = " + "'%s'" %value
    with arcpy.da.SearchCursor(FlightDataPublished, fields, expressionText) as cursor:
        for item in cursor:
            print(item)
            matchedFlightPoints.append(item)
            print("inserted " + item[17] + "into burner layer")
            with arcpy.da.InsertCursor(
                    'C:\\Users\\Micah D Johns\\Documents\\ArcGIS\\Projects\\FlightApp\\FlightApp.gdb\\BurnerLayerToCreateFlightPath',
                    fields) as iCursor:
                for point in matchedFlightPoints:
                    iCursor.insertRow(point)
    arcpy.management.XYTableToPoint("BurnerLayerToCreateFlightPath", r"C:\Users\Micah D Johns\Documents\ArcGIS\Projects\FlightApp\FlightApp.gdb\BurnerLayerToCreateFlightPath_XYTableToPoint","lon", "lat")
    print("xy tabled to points")
    arcpy.management.PointsToLine('BurnerLayerToCreateFlightPath_XYTableToPoint', 'DumpTracks', 'callsign', 'time_position')
    print("points to line")
    arcpy.management.DeleteFeatures('BurnerLayerToCreateFlightPath')
    arcpy.management.DeleteFeatures('BurnerLayerToCreateFlightPath_XYTableToPoint')
    arcpy.management.Append('DumpTracks', 'PublishedTracks', 'NO_TEST')
    print("appended to published tracks")
    arcpy.management.DeleteFeatures('DumpTracks')
    arcpy.management.DeleteIdentical("PublishedTracks", "icao24Callsign", None, 0)


