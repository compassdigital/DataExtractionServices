import csv
import pandas as pd

# Specify the path to your CSV file
file_path = '/Users/yueshengluo/Desktop/google-api/Jimmy Johns_20230919_220358 (1).csv'


#df = pd.read_csv(file_path)
#print(df.head(20))

import gzip

# Specify the path to your gzipped file

# Open the gzipped file for reading
with gzip.open(file_path, mode='rt', encoding='utf-8') as file:
    df = pd.read_csv(file)
print(df.head(20))