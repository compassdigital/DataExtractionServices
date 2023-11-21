import googlemaps
from time import sleep
import pandas as pd
import requests
import numpy as np
import time
import math
import copy
from math import radians, sin, cos, sqrt, atan2

# Replace with your API key
api_key = 'AIzaSyDJqyzXn9u53Oz363RkJe51GyMF2XnWUPA'

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=api_key)

# Specify the location (latitude, longitude) or address, not just ZIP code
location = '32.8695,-117.2173'  # Adjust the location as needed
# search_query = 'restaurants'

#restaurant_categories=['fast food','Chinese restaurant', 'Asian Fusion', 'Japanese restaurant','seafood restaurant','indian restaurant','soul food','Korean restaurant','Mediterranean restaurant','Mexican Restaurant','Middle Eastern Restaurant','Vegetarian Restaurant','Italian restaurant','Fine Dining Restaurant','Pizza','Halal Restaurant']
restaurant_categories = ['restaurant']


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


def place_to_zip(place_id):
    base_url = 'https://maps.googleapis.com/maps/api/place/details/json'

    # Set up the parameters for the request
    params = {
        'place_id': place_id,
        'fields': 'address_components',
        'key': api_key,
    }
    try:
        # Make the Place Details request
        response = requests.get(base_url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            # Find the ZIP code in the address components
            address_components = data['result']['address_components']
            zipcode = next(
                (component['short_name'] for component in address_components if 'postal_code' in component['types']), None)

            if zipcode:
                return zipcode
                print(f"ZIP Code: {zipcode}")
            else:
                print("ZIP Code not found in address components.")
        else:
            print(
                f"Place Details request failed with status: {data['status']}")
    except Exception as e:
        print(f"Error: {e}")

# Initialize a list to store all results


def api_search(location, search_query, radius):
    all_results = []
    zip_code = location['ZIP Code']
    if np.isnan(zip_code):
        return pd.DataFrame()
    latitude = location['Latitude']
    longitude = location['Longitude']
    lat_long = str(latitude)+','+str(longitude)
    #lat_long = '34.042073,-118.254480'
    # print(zip_code)
    # Perform the nearby search
    base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    try:
        '''places_result = gmaps.places_nearby(
            location=lat_long,
            radius=radius,  # You can adjust the radius as needed
            # keyword=search_query,
            # You can specify other types like 'cafe', 'bar', etc.
            type='restaurant',
            # open_now=True,  # To filter by restaurants that are open
            rankby='distance'
        )'''
        params = {
            'location': lat_long,
            'radius': radius,
            'type': 'restaurant',
            #'keyword': search_query,
            #'rankby': 'distance',
            'key': api_key,
        }
        places_result = requests.get(base_url, params=params).json()
        # print(places_result)
        all_results.extend(places_result['results'])
        # while 'next_page_token' in places_result:
        #     # Use the "next_page_token" to request the next set of results
        #     next_page_token = places_result['next_page_token']
        #     sleep(2)
        #     '''
        #     places_result = gmaps.places_nearby(
        #         location=lat_long,
        #         radius=radius,  # You can adjust the radius as needed
        #         keyword=search_query,
        #         # open_now=True,  # To filter by restaurants that are open
        #         page_token=next_page_token,  # Use the next_page_token
        #     )
        #     '''
        #     next_page_params = {
        #         'key': api_key,
        #         'pagetoken': next_page_token
        #     }
        #     places_result = requests.get(base_url, params=next_page_params).json()
        #     all_results.extend(places_result['results'])


        # Print the results
        # for place in places_result['results']:
            # print('----------------------')
            # print(place)
        # print(all_results)
        columns = ['name', 'place_id', 'types', 'price_level',
                   'rating', 'user_ratings_total', 'vicinity']
        df = pd.DataFrame(columns=columns)
        result_df = pd.DataFrame(all_results)
        for col in columns:
            if col in result_df.columns:
                df[col] = result_df[col]
            else:
                df[col] = None
        df["category"] = search_query
        df["zip_code"] = zip_code
        df["latitude"] = latitude
        df["longitude"] = longitude
        #print(zip_code, search_query, len(all_results))
        return df
    except googlemaps.exceptions.ApiError as e:
        print(f"API Error: {e}")

def haversine_distance(coord1, coord2):
    """
    Calculate the Haversine distance between two coordinates.
    """
    # Radius of the Earth in kilometers
    R = 6371.0

    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def is_within_distance(og_location, new_location, og_radius,radius):
    """
    Check if two coordinates are within a certain distance of each other.
    """
    coord1 = (og_location['Latitude'],og_location['Longitude'])
    coord2 = (new_location['Latitude'],new_location['Longitude'])
    distance = haversine_distance(coord1, coord2)*1000
    print(distance)
    return distance-radius <= og_radius


def recurs_search(location,radius, search_query,og_location,og_radius,level):
    print(level,radius,location)
    lat = location['Latitude']
    lon = location['Longitude']
    grid_list= [[0,sqrt(3)/2],
                [0,-sqrt(3)/2],
                [3/4,sqrt(3)/4],
                [-3/4,sqrt(3)/4],
                [-3/4,-sqrt(3)/4],
                [3/4,-sqrt(3)/4],
                [0,0]
                ]
    if level > 3:
        grid_list = [[0.5,0.5],[0.5,-0.5],[-0.5,0.5],[-0.5,-0.5]]
    #if level == 1:
        #grid_list = [[1,1],[1,0],[-1,0],[0,1],[0,0],[0,-1],[-1,-1],[-1,0],[-1,1]]
    final_df = pd.DataFrame()
    spacing = 100
    search_df = api_search(location, search_query, radius+50) 
    print(len(search_df))
    if len(search_df)==20:
        lat_diff = spacing / 111320
        lon_diff =  spacing / (111320 * np.cos(np.radians(lat)))
        for grid in grid_list:
            location['Latitude'] = lat + grid[0]*lat_diff
            location['Longitude'] = lon + grid[1]*lon_diff
            if is_within_distance(og_location, location, og_radius,radius/2):
                if level<=3:
                    search_df = recurs_search(location, radius/2,search_query,og_location,og_radius,level+1)
                else:
                    search_df = recurs_search(location, radius/sqrt(2),search_query,og_location,og_radius,level+1)
                final_df = pd.concat([final_df, search_df])
    else:
        final_df = search_df.copy()
    return final_df.drop_duplicates(subset=['place_id'])

'''
locations = pd.read_csv('grid_coordinates.csv')
final_df  = pd.DataFrame()
for index, location in locations.iterrows():
    for search_query in restaurant_categories:
        category_df = api_search(location,search_query)
        final_df = pd.concat([final_df, category_df])
final_df.to_csv('result.csv', index=False)
'''
start_time = time.time()
final_df = pd.DataFrame()
zip_list = [90014]
radius_list = [800]
#zip_list = [11378,66502,28202,21218,64116]
#radius_list = [2000,10000,300,2000,2000]


for zip, radius in zip(zip_list, radius_list):
    location = zip_to_latlong(zip)
    og_location = copy.deepcopy(location)
    search_df = recurs_search(location,radius,'restaurant',og_location,radius,0)
    final_df = pd.concat([final_df, search_df])


# for zip, radius in zip(zip_list, radius_list):
#     for search_query in restaurant_categories:
#         location = zip_to_latlong(zip) #get lat long info from zipcode
#         category_df = api_search(location, search_query, radius) 
#         final_df = pd.concat([final_df, category_df])


zip_list = []
place_id_list = final_df['place_id'].to_list()

for i in range(len(place_id_list)):
    zip = place_to_zip(place_id_list[i])
    zip_list.append(zip)
    # print(zip,final_df['name'].to_list()[i])

# print(zip_list)
final_df['zip_new'] = zip_list
final_df.to_csv('recursive_test_re.csv', index=False)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Execution time: {elapsed_time} seconds")
