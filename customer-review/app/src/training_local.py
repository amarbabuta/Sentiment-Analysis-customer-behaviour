import pandas as pd
from joblib import dump
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

import json



df = pd.read_csv('app/data/Restaurant_Reviews.tsv', sep='\t')
# Rename columns
df = df.rename(columns={'Review': 'review', 'Liked': 'sentiment'})

dict_json = dict()
dict_json["reviews_table"] = {"data": df.to_dict("records")}
with open('app/data/reviews_data.json', 'w') as f:
    json.dump(dict_json, f)