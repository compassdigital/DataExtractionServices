import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Sample data with zip codes and values to plot
data = pd.read_csv('labled.csv')
#location_info = pd.read_csv('grid_coordinates.csv')
#data.rename(columns={'latitude': 'Latitude'}, inplace=True)
#data = pd.merge(data, location_info, on='Latitude', how='left')
df = data[['Latitude','Longitude','label']]
print(df.head(10))


# Load a shapefile with zip code boundaries
shapefile_path = '/Users/yueshengluo/Desktop/google-api/tl_rd22_06_place.shp'
cali = gpd.read_file(shapefile_path)
#gdf.plot()


geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry)
# Merge your data with the shapefile based on zip codes
gdf.crs = 'EPSG:4326' 
# Create a map plot
min_lat, max_lat = 32, 34.5
min_lon, max_lon = -119, -117
city_min_lat, city_max_lat = 33.6, 34.2
city_min_lon, city_max_lon = -118.5, -118.1
fig, ax = plt.subplots(1, figsize=(12, 8))
ax.set_xlim(city_min_lon, city_max_lon)
ax.set_ylim(city_min_lat, city_max_lat)
cali.boundary.plot(ax=ax, linewidth=1)
gdf.plot(column='label', cmap='coolwarm', markersize=40, ax=ax, legend=True)
ax.set_title('Map with Latitude and Longitude Points')
plt.savefig('cali_k=5.jpg', dpi=300, bbox_inches='tight')
plt.show()