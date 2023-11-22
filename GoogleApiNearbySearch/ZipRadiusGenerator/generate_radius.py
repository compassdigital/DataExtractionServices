import geopandas as gpd
import matplotlib.pyplot as plt
import requests
from geopy.distance import geodesic
import pandas as pd
from shapely.geometry import Point, Polygon, MultiPolygon

def zip_to_latlong(zip_code):
    api_key = 'AIzaSyDJqyzXn9u53Oz363RkJe51GyMF2XnWUPA'

    # Make the API request
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&key={api_key}'

    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            # Extract the latitude and longitude from the API response
            location = data['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            location_obj = {"ZIP Code": zip_code,
                            "Latitude": latitude,
                            "Longitude": longitude}
            # print(f'ZIP Code: {zip_code}')
            # print(f'Latitude: {latitude}')
            # print(f'Longitude: {longitude}')
        else:
            print(f'Error: {data["status"]}')
    else:
        print(f'Error: Request failed with status code {response.status_code}')

    return location_obj  # str(latitude+','+longitude)
# zip_to_latlong('92122')

def calculate_distance(point1, point2):
    return geodesic(point1, point2).meters

def find_farthest_point(geometry, centroid):
    max_distance = 0
    farthest_point = None

    # Check if the geometry is a MultiPolygon
    if isinstance(geometry, Polygon):
        # Iterate over the points in the exterior of the polygon
        for point in geometry.exterior.coords:
            shapely_point = Point(point[0], point[1])
            distance = calculate_distance((centroid.x, centroid.y), (shapely_point.x, shapely_point.y))
            if distance > max_distance:
                max_distance = distance
                farthest_point = shapely_point
    elif isinstance(geometry, MultiPolygon):
        for polygon in geometry.geoms:
            # Iterate over the points in the exterior of each polygon in MultiPolygon
            for point in polygon.exterior.coords:
                shapely_point = Point(point[0], point[1])
                distance = calculate_distance((centroid.x, centroid.y), (shapely_point.x, shapely_point.y))
                if distance > max_distance:
                    max_distance = distance
                    farthest_point = shapely_point

    return farthest_point, max_distance

# Replace 'path_to_your_shapefile' with the actual path to your .shp file
shapefile_path = 'tl_rd22_us_zcta520.shp'

# Load the shapefile using geopandas
data = gpd.read_file(shapefile_path)

# Iterate through each ZIP code geometry
zip_code_list  = []
radius_list = []
counter=0
for index, row in data.iterrows():
    counter += 1
    try:
        zip_code = row['ZCTA5CE20']
        centroid = zip_to_latlong(zip_code)
        
        # Create a Shapely Point for the centroid
        centroid_point = Point(centroid['Longitude'], centroid['Latitude'])
        
        # Calculate the farthest point and its distance from the centroid
        farthest_point, max_distance = find_farthest_point(row['geometry'], centroid_point)
    except Exception as e:
        max_distance = None
        zip_code_list.append(zip_code)
        radius_list.append(max_distance)   
    if counter % 1000 == 0:

        data = {'zip_code': zip_code_list, 'radius': radius_list}
        df = pd.DataFrame(data)
        df.to_csv('zip_radius.csv', index=False)
    print(f"ZIP Code: {zip_code}")
    #print(f"Farthest Point: {farthest_point}")
    print(f"Distance: {max_distance} meters")



# def calculate_min_radius(geometry,zip_code):
#     # Calculate centroid for each geometry
#     center = zip_to_latlong(zip_code)

#     longitude = center['Longitude']
#     latitude = center['Latitude']
#     centroid = Point(longitude, latitude)
    

#     # Find the point farthest from the centroid within the geometry
#     farthest_point = geometry.exterior.interpolate(geometry.exterior.project(centroid))
    
#     # Calculate the distance between centroid and farthest point
#     radius = centroid.distance(farthest_point)
#     # Calculate the radius in degrees (given)
#     radius_degrees = 0.03143352687593537


#     # Create a reference point
#     point1 = (latitude, longitude)

#     # Create a new point by adding the radius to longitude (or latitude)
#     point2 = (latitude, longitude + radius_degrees)

#     # Calculate the distance using geopy
#     distance = geodesic(point1, point2).meters
    
#     return distance

# for index, row in data.iterrows():
#     #zip_code = row['ZIP_CODE'] 
#     print(row)
#     zip_code = row['ZCTA5CE20']
#     print(zip_to_latlong(zip_code))
#     min_radius = calculate_min_radius(row['geometry'],zip_code)
#     print(min_radius)
#     break
    
# min_lat = 33.6
# max_lat = 34.35
# min_lon = -118.8
# max_lon = -118.1

# # Filter the data based on latitude and longitude boundaries
# filtered_data = data.cx[min_lon:max_lon, min_lat:max_lat]

# # Plotting the filtered boundaries
# filtered_data.plot(edgecolor='black', figsize=(10, 10))
# plt.title('Filtered ZIP Code Boundaries')
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.show()