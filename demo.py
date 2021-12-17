# from poivizdynamic import poivizdynamic as pv
import poivizdynamic as pv

import pandas as pd


# .src/poivizdynamic/data/demo_fake_data.csv')
df = pd.read_csv("src/poivizdynamic/data/demo_fake_data.csv")

travel = pv.get_demo_data(df, "my travel map")

life = pv.get_demo_data(df, "life log")

starb = pv.get_demo_data(df, "starbuck")


travel = pv.get_geo_dataset(travel)
travel = pv.clean_dataset(travel)

travel.head()

pv.get_footprint_map(travel)


# pv.get_animated_bubble_map(starb, zoom = 10, color_value_discrete = False, bubble_size = "interest_value", color_group_lab = "spot_name")
