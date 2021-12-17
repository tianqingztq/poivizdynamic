import requests
import pandas as pd
from statistics import median
import os
# from requests_oauthlib import OAuth1Session
import time
from datetime import datetime, timedelta
# from dateutil import rrule
import warnings

import plotly.graph_objects as go
import plotly.express as px


def get_coordinate_api(dataframe, maptype = "world"):
    start = time.time()  # time in seconds
    
    addr = dataframe[["street","city",'state',"country"]].values.tolist()[0]
        
    if maptype == "world":
        
        #GEO_RADAR_API_KEY=os.getenv('GEO_RADAR_API_KEY')
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
            #return out_df
    elif maptype == "US":
        GEO_CENSUS_API_KEY=os.getenv('GEO_CENSUS_API_KEY')
        api_key = GEO_CENSUS_API_KEY
        
        street, city, state, _ = addr
        
        benchmark = 'Public_AR_Census2020'
        vintage = 'Census2020_Census2020'
        layers = '10'
        api_url = f'https://geocoding.geo.census.gov/geocoder/geographies/address?street={street}&city={city}&state={state}&benchmark={benchmark}&vintage={vintage}&layers={layers}&format=json&key={api_key}'
        try:
            r = requests.get(api_url)
            # If the response was successful, no Exception will be raised
            r.raise_for_status()
        except requests.exceptions.RequestException as http_err:
            print(f'Error occurred:{http_err}')
        else:
            #json_output = json.loads(r.content) 
            print('Successful! Status Code:{}'.format(r.status_code))
            df = pd.DataFrame(r.json()["result"]["addressMatches"])
            if df.empty == True:
                warnings.warn("Sorry! This address cannot be searched through census_geocoding api and returned an empty result")
                return None
            else:
                cord = df["coordinates"].values.tolist()
                cord_split = pd.DataFrame(cord, columns = ['x','y'])
                adds = df["addressComponents"].values.tolist()
                #adds_split = pd.DataFrame(adds, columns = ['city', 'state', 'zip'])
                #out_df = pd.concat([df, cord_split, adds_split],axis=1)
                out_df = pd.concat([df, cord_split],axis=1)[["y","x","matchedAddress"]]
                out_df.columns = ["latitude", "longitude", "formattedAddress"]
                end = time.time()
                print(f'Requested the api and transformed into dataframe in {end - start:0.4f} seconds')
    
    return out_df



  
def get_geo_dataset(df, maptype = "world"):
    # use api
    # apply api only on unique address
    temp_nodup = df.drop_duplicates(subset=['street', 'city'])
    
    for i in range(len(temp_nodup)):
        temp = temp_nodup.iloc[i,:]
        temp = pd.DataFrame([temp.values],columns = temp.index)
        
        
        temp2 = get_coordinate_api(temp,maptype = maptype)
        if i == 0:
            df_out = pd.concat([temp, temp2], axis=1)
        else:
            if temp2 is None:
                continue
            else:

                mid = pd.concat([temp, temp2], axis=1)
                df_out = df_out.append(mid, ignore_index=True) 
                

        i += 1
        
    # left join the list of outcome to the original dataset (with duplicates)
    df_out_final = df.merge(df_out[['street','city','state',"latitude", "longitude", "formattedAddress"]], on=['street','city','state'], how = 'left')

    return df_out_final


def clean_dataset(df):
    df['date'] = pd.to_datetime(df["date"])
    df['longitude'] = pd.to_numeric(df["longitude"])  # ,errors = 'coerce'
    df['latitude'] = pd.to_numeric(df["latitude"])
    df = df.sort_values(by = 'date')
    return df
  

def get_footprint_map(df_in, fig_name = 'my_animate_map', title_text = "My animated map", title_size = 20, zoom = 2.5):
    # https://docs.mapbox.com/help/getting-started/access-tokens/

    TOKEN_MAPBOX = os.getenv('TOKEN_MAPBOX')
    

    lon = [df_in["longitude"][0]]
    lat = [df_in["latitude"][0]]
    
    mid_lat = df_in["latitude"].mean()
    mid_lon = df_in["longitude"].mean()
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
            'style': "light", 'zoom': zoom},
        ),
        
        frames = frames
    )
    

    fig.update_layout(
                    mapbox_center = {"lat": mid_lat, "lon": mid_lon},
                    margin={"r":0,"t":40,"l":0,"b":0},
                    title_text = title_text,
                    title_font_size = title_size
                      
                     )

    
    # fig.show()
    
    # save the html dynamic file
    if not os.path.exists('demo_output'):
        os.makedirs('demo_output')

    html_path = f'demo_output/{fig_name}.html'
    #html_path = f'{fig_name}.html'
    fig.write_html(html_path)
    return fig

# bubble plot
# bubble plot
def get_animated_bubble_map(df, title_text = "My animated bubble map with value/ colored with spot or group", title_size = 20, color_group_lab = "spot_name", color_value_discrete = True, bubble_size = "interest_value", radius:'int > 0' = 20, zoom = 2.5, fig_name = "my_animated_bubble_plot")-> None:

    df = df.dropna(subset = ["longitude", "latitude"],axis=0)

    lat_lab = "latitude"
    lon_lab = "longitude"
   
    date = df["date"].apply(lambda x: x.strftime('%Y-%m-%d'))
    
    mid_lat = median(df[lat_lab])

    mid_lon = median(df[lon_lab])
    
    if type(bubble_size) == str:
        
        df[bubble_size] = df[bubble_size].apply(lambda x: pd.to_numeric(x))
        print("bubble_size will change along with the true value")
    else:
        const_num = bubble_size
        bubble_size = [const_num] * len(df)
        print("bubble_size is a constant number")

    if color_value_discrete == True:
        print("the value is discrete")
        fig = px.scatter_mapbox(df, lat = lat_lab,
                                lon = lon_lab,
                                size = bubble_size,
                                color = color_group_lab,
                                animation_frame = date,
                                color_discrete_sequence = px.colors.qualitative.D3,  
                                # https://plotly.com/python/discrete-color/
                                size_max = radius,
                                # labels = {value_lab:'income'} # only for continuous data
                               )
    else:
        print("the value is continuous")
        fig = px.scatter_mapbox(df, lat = lat_lab,
                                lon = lon_lab,
                                size = bubble_size,
                                color = color_group_lab,
                                animation_frame = date,
                                color_continuous_scale=px.colors.cyclical.IceFire,
                                #color_continuous_scale=px.colors.sequential.Viridis,
                                #color_discrete_sequence = px.colors.qualitative.D3,  
                                # https://plotly.com/python/discrete-color/
                                size_max = radius,
                                # labels = {value_lab:'income'} # only for continuous data
                               )
    fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom=zoom, 
                      mapbox_center = {"lat": mid_lat, "lon": mid_lon},
                      
                     )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    fig.update_layout(title_text = title_text, title_font_size = title_size)
    
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 600
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 600
    fig.layout.coloraxis.showscale = True   
    fig.layout.sliders[0].pad.t = 10
    fig.layout.updatemenus[0].pad.t= 10 
    
    # save the html dynamic file
    if not os.path.exists('demo_output'):
        os.makedirs('demo_output')

    html_path = f'demo_output/{fig_name}.html'
    #html_path = f'{fig_name}.html'
    fig.write_html(html_path)
    
    return fig




def get_demo_data(df, demo_data = "my travel map"):
    if demo_data == "my travel map":
        df = df.iloc[0:4,]
    elif demo_data == "life log":
        df = df.iloc[4:7,]
    elif demo_data == "starbuck":
        df = df.iloc[7:,]
    return df