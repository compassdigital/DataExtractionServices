import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests

api_key = 'AIzaSyDJqyzXn9u53Oz363RkJe51GyMF2XnWUPA'
def get_zip(lat,lon):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}'
    try:
        response = requests.get(url)
        data = response.json()
        if data['status'] == 'OK':
            # Extract the ZIP code from the results
            for result in data['results']:
                for component in result['address_components']:
                    if 'postal_code' in component['types']:
                        zip_code = component['long_name']
                        print(f'ZIP Code: {zip_code}')
                        return zip_code
                        
        else:
            print(f'Geocoding request failed with status: {data["status"]}')
    except Exception as e:
        print(f'Error: {e}')
# Load a shapefile or GeoDataFrame that represents the boundary of Los Angeles
# Replace 'your_shapefile.shp' with the actual path to your Los Angeles boundary data
boundary_gdf = gpd.read_file('/Users/yueshengluo/Desktop/google-api/tl_rd22_06_place.shp')

# Define the grid spacing (2000 meters)
grid_spacing = 2000  # in meters

# Calculate the bounding box of Los Angeles
min_lon, min_lat, max_lon, max_lat = boundary_gdf.total_bounds
# Create a map plot
city_min_lat, city_max_lat = 33.4, 34.2
city_min_lon, city_max_lon = -118.6, -117.5
# Create lists to store latitude and longitude coordinates
latitudes = []
longitudes = []
zipcode = []

# Generate coordinates within the boundary
for lat in np.arange(min_lat, max_lat, grid_spacing / 111320):  # 1 degree of latitude is approximately 111320 meters
    for lon in np.arange(min_lon, max_lon, grid_spacing / (111320 * np.cos(np.radians(lat)))):
        # Check if the generated point is within the boundary
        point = Point(lon, lat)
        if boundary_gdf.geometry.contains(point).any():
            if lat > city_min_lat and lat < city_max_lat and lon > city_min_lon and lon < city_max_lon:
                latitudes.append(lat)
                longitudes.append(lon)
                #zipcode.append(get_zip(lat,lon))
                


# Create a DataFrame with the generated coordinates
#grid_df = pd.DataFrame({'ZIP Code': zipcode,'Longitude': longitudes, 'Latitude': latitudes})
grid_df = pd.DataFrame({'Longitude': longitudes, 'Latitude': latitudes})

# Save the DataFrame as a CSV file
# Replace 'grid_coordinates.csv' with the desired output CSV filename
grid_df.to_csv('grid_coordinates_demo.csv', index=False)

# Display the first few rows of the generated grid
print(grid_df.head())

# Convert the DataFrame to a GeoDataFrame with Point geometry
geometry = [Point(lon, lat) for lon, lat in zip(grid_df['Longitude'], grid_df['Latitude'])]
gdf = gpd.GeoDataFrame(grid_df, geometry=geometry)


fig, ax = plt.subplots(figsize=(12, 12))
ax.set_xlim(city_min_lon, city_max_lon)
ax.set_ylim(city_min_lat, city_max_lat)
boundary_gdf.plot(ax=ax, color='lightgray', edgecolor='black', alpha=0.5)
gdf.plot(ax=ax, markersize=2, color='blue', alpha=0.7)

# Set axis labels and title
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Grid of Coordinates in Los Angeles')

# Show the map
plt.show()
plt.savefig('demo.jpg')