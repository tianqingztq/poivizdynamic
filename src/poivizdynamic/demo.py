from poivizdynamic import poivizdynamic as pv

import pandas as pd
import os
print(os.getcwd())

df = pd.read_csv('./data/demo_fake_data.csv')

travel = pv.get_demo_data(df, "my travel map")

life = pv.get_demo_data(df, "life log")

starb = pv.get_demo_data(df, "starbuck")


travel = pv.get_geo_dataset(travel)
travel = pv.clean_dataset(travel)

travel.head()

pv.get_footprint_map(travel)