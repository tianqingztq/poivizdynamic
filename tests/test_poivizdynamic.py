from poivizdynamic import poivizdynamic as pv
from poivizdynamic import __version__
import os
import pandas as pd

df = pd.read_csv("src/poivizdynamic/data/demo_fake_data.csv")
travel = pv.get_demo_data(df, "my travel map")


def test_version():
    assert __version__ == "0.1.7"


def test_get_geo_dataset_preprocess(df=travel):
    api_key_us = os.getenv("GEO_CENSUS_API_KEY")
    df_us = pv.get_geo_dataset(api_key_us, df, maptype="us")
    assert df_us.shape[1] == 12

    api_key_w = os.getenv("GEO_RADAR_API_KEY")
    df_world = pv.get_geo_dataset(api_key_w, df, maptype="world")
    assert df_world.shape[1] == 12

    df_world = pv.clean_dataset(df_world)
    assert df_world.dtypes["interest_value"] in [int, float]
    assert df_world.dtypes["latitude"] in [int, float]
    assert df_world.dtypes["longitude"] in [int, float]
