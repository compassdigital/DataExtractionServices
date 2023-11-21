import requests

# Replace 'YOUR_API_KEY' with your actual Google Maps API key
api_key = 'AIzaSyDJqyzXn9u53Oz363RkJe51GyMF2XnWUPA'

# Replace 'LATITUDE' and 'LONGITUDE' with the coordinates you want to look up
latitude = 44.763706
longitude = -106.940227

# Make the reverse geocoding request
url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}&enable_address_descriptor=true'

try:
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        # Extract and display address components
        for result in data['results']:
            #print("Formatted Address:", result['formatted_address'])
            for component in result['address_components']:
                component_type = ', '.join(component['types'])
                #print(f"{component_type}: {component['long_name']}")
        print("\n")
        print(data)
    else:
        print(f'Geocoding request failed with status: {data["status"]}')
except Exception as e:
    print(f'Error: {e}')