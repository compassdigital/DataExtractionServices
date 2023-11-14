import googlemaps
from time import sleep
import pandas as pd
import requests
import numpy as np
import time

# Replace with your API key
api_key = 'AIzaSyDJqyzXn9u53Oz363RkJe51GyMF2XnWUPA'

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=api_key)

# Specify the location (latitude, longitude) or address, not just ZIP code
location = '32.8695,-117.2173'  # Adjust the location as needed
# search_query = 'restaurants'

restaurant_categories=['fast food','Chinese restaurant', 'Asian Fusion', 'Japanese restaurant','seafood restaurant','indian restaurant','soul food','Korean restaurant','Mediterranean restaurant','Mexican Restaurant','Middle Eastern Restaurant','Vegetarian Restaurant','Italian restaurant','Fine Dining Restaurant','Pizza','Halal Restaurant']
#restaurant_categories = ['mom Spaghetti']


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
            #'type': 'restaurant',
            'keyword': search_query,
            #'rankby': 'distance',
            'key': api_key,
        }
        places_result = requests.get(base_url, params=params).json()
        # print(places_result)
        all_results.extend(places_result['results'])
        while 'next_page_token' in places_result:
            # Use the "next_page_token" to request the next set of results
            next_page_token = places_result['next_page_token']
            sleep(2)
            '''
            places_result = gmaps.places_nearby(
                location=lat_long,
                radius=radius,  # You can adjust the radius as needed
                keyword=search_query,
                # open_now=True,  # To filter by restaurants that are open
                page_token=next_page_token,  # Use the next_page_token
            )
            '''
            next_page_params = {
                'key': api_key,
                'pagetoken': next_page_token
            }
            places_result = requests.get(base_url, params=next_page_params).json()
            all_results.extend(places_result['results'])
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
        print(zip_code, search_query, len(all_results))
        return df
    except googlemaps.exceptions.ApiError as e:
        print(f"API Error: {e}")


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
#zip_list = [11378,66502,28202,21218,64116]
#radius_list = [2000,10000,300,2000,2000]
zip_list = [90014]
radius_list = [500]
for zip, radius in zip(zip_list, radius_list):
    for search_query in restaurant_categories:
        location = zip_to_latlong(zip)
        category_df = api_search(location, search_query, radius)
        final_df = pd.concat([final_df, category_df])
zip_list = []
place_id_list = final_df['place_id'].to_list()
for i in range(len(place_id_list)):
    zip = place_to_zip(place_id_list[i])
    zip_list.append(zip)
    # print(zip,final_df['name'].to_list()[i])


# print(zip_list)
final_df['zip_new'] = zip_list
final_df.to_csv('result_5_zips_dis_1.csv', index=False)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Execution time: {elapsed_time} seconds")
