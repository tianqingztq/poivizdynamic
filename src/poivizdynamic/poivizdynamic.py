import requests
import pandas as pd
import os
# from requests_oauthlib import OAuth1Session
import geopandas as gpd
import time
from datetime import datetime, timedelta
# from dateutil import rrule
import numpy as np
import warnings

import plotly.graph_objects as go


def get_coordinate_api(addr):
    start = time.time()  # time in seconds
    GEO_RADAR_API_KEY=os.getenv('GEO_RADAR_API_KEY')
    api_key = GEO_RADAR_API_KEY
    api_url = f'https://api.radar.io/v1/geocode/forward?query={addr}'
    try:
        r = requests.get(api_url, headers = {"Authorization": api_key})
        # If the response was successful, no Exception will be raised
        r.raise_for_status()
    except requests.exceptions.RequestException as http_err:
        print(f'Error occurred:{http_err}')
    else:
        #json_output = json.loads(r.content) 
        print('Successful! Status Code:{}'.format(r.status_code))
        out_df = pd.DataFrame(r.json()["addresses"])[["latitude","longitude","formattedAddress"]]
        if out_df.empty == True:
            warnings.warn("Sorry! This address cannot be searched through the api and returned an empty result")
            return None
        else:
            end = time.time()
            print(f'Requested the api in {end - start:0.4f} seconds')
            return out_df

# get_coordinate_api('20 Jay Street, Brooklyn, New York, NY')
    


def get_demo_data(df, demo_data = "my travel map"):
    if demo_data == "my travel map":
        df = df.iloc[0:4,]
    elif demo_data == "life log":
        df = df.iloc[4:7,]
    elif demo_data == "starbuck":
        df = df.iloc[7:,]
    return df


def clean_dataset(df):
    df['date'] = pd.to_datetime(df["date"])
    df['longitude'] = pd.to_numeric(df["longitude"])  # ,errors = 'coerce'
    df['latitude'] = pd.to_numeric(df["latitude"])
    df = df.sort_values(by = 'date')
    return df
    
def get_geo_dataset(df):
    # use api
    # apply api only on unique address
    temp_nodup = df.drop_duplicates(subset=['street', 'city'])
    for i in range(len(temp_nodup)):
        temp = temp_nodup.iloc[i,:]
        temp = pd.DataFrame([temp.values],columns = temp.index)
        adds_ls = temp[["street","city",'state',"country"]].values.tolist()
        
        temp2 = get_coordinate_api(adds_ls[0])
        if i == 0:
            df_out = pd.concat([temp, temp2], axis=1)
        else:

            mid = pd.concat([temp, temp2], axis=1)
            df_out = df_out.append(mid, ignore_index=True) 

        i += 1
    return df_out


def get_footprint_map(df_in, fig_name = 'my_animate_map', zoom = 2.5):
    # https://docs.mapbox.com/help/getting-started/access-tokens/

    TOKEN_MAPBOX = os.getenv('TOKEN_MAPBOX')

    lon = [df_in["longitude"][0]]
    lat = [df_in["latitude"][0]]
    
    mid_lat = np.mean(df_in["latitude"])
    mid_lon = np.mean(df_in["longitude"])
    lon_ls = df_in["longitude"].values.tolist()
    lat_ls = df_in["latitude"].values.tolist()
    
    frames = []
    
    for i in range(1,len(df_in)):
 
        lon.append(lon_ls[i])

        lat.append(lat_ls[i])

        framei = go.Frame(data=[
                go.Scattermapbox(
                    lon = lon,
                    lat = lat,
                 )],    
                         )
        frames.append(framei)

    fig = go.Figure(
        data = [
            go.Scattermapbox(
                mode = "markers+text+lines",
                lon = lon_ls,
                lat = lat_ls,
                marker = {'size': 20, 
                          'symbol': df_in["symbol"].tolist()},
                text = df_in["spot_name"].tolist(),

                textposition = 'bottom right'
                # symbols: https://labs.mapbox.com/maki-icons/
            )
        ],

        layout = go.Layout(
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None])])],
            mapbox = {
            'accesstoken': TOKEN_MAPBOX,
            'style': "light", 'zoom': zoom}
        ),
        
        frames = frames
    )
    

    fig.update_layout(
                    mapbox_center = {"lat": mid_lat, "lon": mid_lon},
                    margin={"r":0,"t":0,"l":0,"b":0}
                      
                     )


    fig.show()
    html_path = f'/output/{fig_name}.html'
    fig.write_html(html_path)
