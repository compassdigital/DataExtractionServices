import pandas as pd
#import numpy as np
#from sklearn.cluster import KMeans
#import matplotlib.pyplot as plt
zip_set = [11378,66502,28202,21218,64116]
final_df = pd.read_csv('result_5_zips_dis_1.csv')
zip_list = final_df['zip_code'].to_list()
new_zip = final_df['zip_new'].to_list()
common_count = 0
for i in range(len(zip_list)):
  #print(zip_list[i],new_zip[i])

  if zip_list[i] == new_zip[i]:
    common_count += 1
print(common_count)
print(common_count/len(new_zip))

filtered_df = final_df[final_df['zip_code'] == final_df['zip_new']]
filtered_df.to_csv('result_5_zips_dis_filtered_1.csv')
'''
cleaned_df = raw_df.drop_duplicates(
  subset = ['place_id', 'zip_code'],
  keep = 'last').reset_index(drop = True)
cleaned_df.to_csv('cleaned_result.csv')
#grouped_df_category = raw_df.groupby(['latitude','longitude'])['category'].value_counts().unstack(fill_value=0)
#grouped_df_price = raw_df.groupby(['latitude','longitude'])['price_level'].value_counts().unstack(fill_value=0)
grouped_df_category = raw_df.groupby('zip_code')['category'].value_counts().unstack(fill_value=0)
grouped_df_price = raw_df.groupby(['zip_code'])['price_level'].value_counts().unstack(fill_value=0)
grouped_df = pd.concat([grouped_df_category, grouped_df_price], axis=1)
grouped_df.columns = grouped_df.columns.astype(str)
grouped_df = grouped_df.fillna(0)
#print(grouped_df)

# Number of clusters (you can choose an appropriate value)
k = 3

# Create a KMeans instance
kmeans = KMeans(n_clusters=k, random_state=42)
# Fit the KMeans model to your DataFrame
kmeans.fit(grouped_df)
# Get cluster labels for each data point
cluster_labels = kmeans.labels_
grouped_df['label'] = cluster_labels
grouped_df.to_csv('labled_zipcode.csv')
'''