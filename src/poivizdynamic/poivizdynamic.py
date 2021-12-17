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


def get_coordinate_api(api_key, dataframe, maptype="world"):
    """
    This function returns a one-line pandans.DataFrame showing coordination information of a POI.

    Parameters
    ---
    api_key: a private api key
        if maptype = "US":
            pass in the private api key GEO_CENSUS_API_KEY provided by the U.S. Census Bureau. https://www.census.gov/data/developers/data-sets/popest-popproj/popest.html
        if maptype = "wold":
            pass in the private api key GEO_RADAR_API_KEY provided by Radar (Radar is the leading geofencing and location tracking platform). Instruction on how to get the code at Authentication session: https://radar.com/documentation/api

    dataframe : pandans.DataFrame
        This is the input one-line dataframe, which used as the query text for the geo-APIs.
        It should contain the address information for only one POI.

    maptype : {"world", "US"}, default "world", optional
        Geo-API to use. The "US" API returns more accurate result than "world" when specifically looking at places in the US.
        Details provided in the links attached below the api_key description.

    Returns
    ---
    Output one-line pandans.DataFrame showing coordination information of a POI with latitude, longitude, and formattedAddress.
    latitude            float64
    longitude           float64
    formattedAddress     object

    Example
    ---
    get_coordinate_api(api_key = GEO_CENSUS_API_KEY, dataframe, maptype = "US")
    get_coordinate_api(api_key = GEO_RADAR_API_KEY, dataframe, maptype = "world")

    """

    start = time.time()  # time in seconds

    addr = dataframe[["street", "city", "state", "country"]].values.tolist()[0]

    if maptype == "world":

        # GEO_RADAR_API_KEY = os.getenv("GEO_RADAR_API_KEY")
        # api_key = GEO_RADAR_API_KEY
        api_url = f"https://api.radar.io/v1/geocode/forward?query={addr}"
        try:
            r = requests.get(api_url, headers={"Authorization": api_key})
            # If the response was successful, no Exception will be raised
            r.raise_for_status()
        except requests.exceptions.RequestException as http_err:
            print(f"Error occurred:{http_err}")
        else:
            # json_output = json.loads(r.content)
            print("Successful! Status Code:{}".format(r.status_code))
            out_df = pd.DataFrame(r.json()["addresses"])[
                ["latitude", "longitude", "formattedAddress"]
            ]
            if out_df.empty == True:
                warnings.warn(
                    "Sorry! This address cannot be searched through the api and returned an empty result"
                )
                return None
            else:
                end = time.time()
                print(f"Requested the api in {end - start:0.4f} seconds")
            # return out_df
    elif maptype == "US":
        # GEO_CENSUS_API_KEY = os.getenv("GEO_CENSUS_API_KEY")
        # api_key = GEO_CENSUS_API_KEY

        street, city, state, _ = addr

        benchmark = "Public_AR_Census2020"
        vintage = "Census2020_Census2020"
        layers = "10"
        api_url = f"https://geocoding.geo.census.gov/geocoder/geographies/address?street={street}&city={city}&state={state}&benchmark={benchmark}&vintage={vintage}&layers={layers}&format=json&key={api_key}"
        try:
            r = requests.get(api_url)
            # If the response was successful, no Exception will be raised
            r.raise_for_status()
        except requests.exceptions.RequestException as http_err:
            print(f"Error occurred:{http_err}")
        else:
            # json_output = json.loads(r.content)
            print("Successful! Status Code:{}".format(r.status_code))
            df = pd.DataFrame(r.json()["result"]["addressMatches"])
            if df.empty == True:
                warnings.warn(
                    "Sorry! This address cannot be searched through census_geocoding api and returned an empty result"
                )
                return None
            else:
                cord = df["coordinates"].values.tolist()
                cord_split = pd.DataFrame(cord, columns=["x", "y"])
                # adds = df["addressComponents"].values.tolist()
                # adds_split = pd.DataFrame(adds, columns = ['city', 'state', 'zip'])
                # out_df = pd.concat([df, cord_split, adds_split],axis=1)
                out_df = pd.concat([df, cord_split], axis=1)[
                    ["y", "x", "matchedAddress"]
                ]
                out_df.columns = ["latitude", "longitude", "formattedAddress"]
                end = time.time()
                print(
                    f"Requested the api and transformed into dataframe in {end - start:0.4f} seconds"
                )

    return out_df


def get_geo_dataset(api_key, df, maptype="world"):
    """
    This function returns a whole dataset with geo-information, a pandans.DataFrame combined original information with matched geographical information.

    Parameters
    ---
    api_key: a private api key (pass the api key to the inner function get_coordinate_api(); same help doc of that one).
        if maptype = "US":
            pass in the private api key GEO_CENSUS_API_KEY provided by the U.S. Census Bureau. https://www.census.gov/data/developers/data-sets/popest-popproj/popest.html
        if maptype = "wold":
            pass in the private api key GEO_RADAR_API_KEY provided by Radar (Radar is the leading geofencing and location tracking platform). Instruction on how to get the code at Authentication session: https://radar.com/documentation/api

    dataframe : pandans.DataFrame
        This is the input dataframe, which contains a list of POI's address information.

    maptype : {"world", "US"}, default "world", optional
        Geo-API to use. The "US" API returns more accurate result than "world" when specifically looking at places in the US.
        Details provided in the links attached below the api_key description.

    Returns
    ---
    Output the whole dataset with geo-information, a pandans.DataFrame combined original information with matched geographical information.
    The column number should be 12.

    unique_id             int64
    spot_name            object
    street               object
    city                 object
    state                object
    country              object
    interest_value        int64
    date                 object
    symbol               object
    latitude            float64
    longitude           float64
    formattedAddress     object
    dtype: object

    Example
    ---
    get_coordinate_api(api_key = GEO_RADAR_API_KEY, travel, maptype = "world")
    get_coordinate_api(api_key = GEO_CENSUS_API_KEY, starbuck, maptype = "US")

    """

    # apply api only on unique address in oreder to save time and even money.
    # get non-duplication dataset
    temp_nodup = df.drop_duplicates(subset=["street", "city"])

    for i in range(len(temp_nodup)):
        temp = temp_nodup.iloc[i, :]
        temp = pd.DataFrame([temp.values], columns=temp.index)

        temp2 = get_coordinate_api(api_key, temp, maptype=maptype)
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
    df_out_final = df.merge(
        df_out[
            ["street", "city", "state", "latitude", "longitude", "formattedAddress"]
        ],
        on=["street", "city", "state"],
        how="left",
    )

    return df_out_final


def clean_dataset(df):
    """
    This function gets ready the data type in the dataset for animated map ploting usage.
    It ensures the "date" is date format; "longitude" and "latitude" are numeric format.

    Parameters
    ---
    dataframe : pandans.DataFrame
        This is the input dataframe.

    Returns
    ---
    Output dataframe has dypes as follows:

    unique_id                    int64
    spot_name                   object
    street                      object
    city                        object
    state                       object
    country                     object
    interest_value               int64
    date                datetime64[ns]
    symbol                      object
    latitude                   float64
    longitude                  float64
    formattedAddress            object
    dtype: object

    """
    df["date"] = pd.to_datetime(df["date"])
    df["longitude"] = pd.to_numeric(df["longitude"])  # ,errors = 'coerce'
    df["latitude"] = pd.to_numeric(df["latitude"])
    df = df.sort_values(by="date")
    return df


def get_footprint_map(
    TOKEN_MAPBOX,
    df_in,
    fig_name="my_animate_map",
    title_text="My animated map",
    title_size=20,
    zoom=2.5,
):
    """
    This function returns a dynamic footprint plotly map plot saved as "html" file in the "demo_output" directory.

    Parameters
    ---
    TOKEN_MAPBOX: an access token is required by Mapbox in order to get the dynamic plot look nicer.
        Free access for the token: https://docs.mapbox.com/help/getting-started/access-tokens/.
    df_in:  pd.DataFrame
        The dataframe contains the information would be animated and mapped.
    fig_name: str, default "my_animate_map"
        Customize name of saving html file.
    title_text: str, default "My animated map"
        Customize name of the map title.
    title_size: int, default 20
        Customize the font size of the map title.
    zoom: float/ int, default 2.5
        Customize the zoom level of the map plot. 2.5 for country level, 10~20 for city/ street level.

    Returns
    ---
    Output plotly dynamic map plot of the POIs' geometric information change with the date information. Trace line of the activity is shown.

    Example
    ---
    get_footprint_map(TOKEN_MAPBOX, travel, fig_name = "my foot print", title_text = "My Animated Footprint Map")

    """

    # TOKEN_MAPBOX = os.getenv("TOKEN_MAPBOX")

    lon = [df_in["longitude"][0]]
    lat = [df_in["latitude"][0]]

    mid_lat = df_in["latitude"].mean()
    mid_lon = df_in["longitude"].mean()
    lon_ls = df_in["longitude"].values.tolist()
    lat_ls = df_in["latitude"].values.tolist()

    frames = []

    for i in range(1, len(df_in)):

        lon.append(lon_ls[i])

        lat.append(lat_ls[i])

        framei = go.Frame(
            data=[
                go.Scattermapbox(
                    lon=lon,
                    lat=lat,
                )
            ],
        )
        frames.append(framei)

    fig = go.Figure(
        data=[
            go.Scattermapbox(
                mode="markers+text+lines",
                lon=lon_ls,
                lat=lat_ls,
                marker={"size": 20, "symbol": df_in["symbol"].tolist()},
                text=df_in["spot_name"].tolist(),
                textposition="bottom right"
                # symbols: https://labs.mapbox.com/maki-icons/
            )
        ],
        layout=go.Layout(
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[dict(label="Play", method="animate", args=[None])],
                )
            ],
            mapbox={"accesstoken": TOKEN_MAPBOX, "style": "light", "zoom": zoom},
        ),
        frames=frames,
    )

    fig.update_layout(
        mapbox_center={"lat": mid_lat, "lon": mid_lon},
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text=title_text,
        title_font_size=title_size,
    )

    fig.show()

    # save the html dynamic file
    if not os.path.exists("demo_output"):
        os.makedirs("demo_output")

    html_path = f"demo_output/{fig_name}.html"
    # html_path = f'{fig_name}.html'
    fig.write_html(html_path)
    # return fig


def get_animated_bubble_map(
    df,
    title_text="My animated bubble map with value/ colored with spot or group",
    title_size=20,
    color_group_lab="spot_name",
    color_value_discrete=True,
    bubble_size="interest_value",
    radius=20,
    zoom=2.5,
    fig_name="my_animated_bubble_plot",
):
    """
    This function returns a dynamic bubble plotly map plot saved as "html" file in the "demo_output" directory. The bubble size and color could be controlled.
    More customized parameters are still under exploration due to the time limitation...

    Parameters
    ---
    df: pd.DataFrame
        The dataframe contains the information would be animated and mapped.
    title_text: str, default "My animated map"
        Customize name of the map title.
    title_size: int, default 20
        Customize the font size of the map title.
    color_group_lab: str, default "spot_name"
        This control the color group, which means the color will be group by color_group_lab.
    color_value_discrete: bool, default True
        True: the color value is continuous, so the color bar will be set in a continous form.
        False: the color value is discrete, so the color will be categorical set.
    bubble_size: str -> name of column, or int -> constant bubble_size; default "interest_value"
        Can be the name of column with dynamic values, and the bubble size will change along with the change of the dynamic values given.
        If the bubble_size input is an instant, the bubble size will remain the same during the whole time-series process shown on the plot.
    radius: int, default 20
        Customize the radius of the bubble.
    zoom: float/ int, default 2.5
        Customize the zoom level of the map plot. 2.5 for country level, 10~20 for city/ street level.
    fig_name: str, default "my_animate_map"
        Customize name of saving html file.

    Returns
    ---
    Output plotly dynamic bubble map plot of the POIs' geometric information change with the date information.

    Example
    ---
    get_animated_bubble_map(TOKEN_MAPBOX, starb2, zoom = 10, color_value_discrete = False, bubble_size = "interest_value", color_group_lab = "interest_value", fig_name = "starbuck2")

    """
    df = df.dropna(subset=["longitude", "latitude"], axis=0)

    lat_lab = "latitude"
    lon_lab = "longitude"

    date = df["date"].apply(lambda x: x.strftime("%Y-%m-%d"))

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
        fig = px.scatter_mapbox(
            df,
            lat=lat_lab,
            lon=lon_lab,
            size=bubble_size,
            color=color_group_lab,
            animation_frame=date,
            color_discrete_sequence=px.colors.qualitative.D3,
            # https://plotly.com/python/discrete-color/
            size_max=radius,
            # labels = {value_lab:'income'} # only for continuous data
        )
    else:
        print("the value is continuous")
        fig = px.scatter_mapbox(
            df,
            lat=lat_lab,
            lon=lon_lab,
            size=bubble_size,
            color=color_group_lab,
            animation_frame=date,
            color_continuous_scale=px.colors.sequential.Mint,
            # color_continuous_scale=px.colors.cyclical.IceFire,
            # color_continuous_scale=px.colors.sequential.Viridis,
            # color_discrete_sequence = px.colors.qualitative.D3,
            # https://plotly.com/python/discrete-color/
            size_max=radius,
            # labels = {value_lab:'income'} # only for continuous data
        )
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=zoom,
        mapbox_center={"lat": mid_lat, "lon": mid_lon},
    )
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    fig.update_layout(title_text=title_text, title_font_size=title_size)

    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 600
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 600
    fig.layout.coloraxis.showscale = True
    fig.layout.sliders[0].pad.t = 10
    fig.layout.updatemenus[0].pad.t = 10

    fig.show()

    # save the html dynamic file
    if not os.path.exists("demo_output"):
        os.makedirs("demo_output")

    html_path = f"demo_output/{fig_name}.html"
    # html_path = f'{fig_name}.html'
    fig.write_html(html_path)

    # return fig


def get_demo_data(df, demo_data="my travel map"):
    """
    This function gets the three demo datasets.

    Parameters
    ---
    dataframe : pandans.DataFrame
        This is the input dataframe named "demo_fake_data".

    demo_data: {"my travel map", "life log", "starbuck"}, default "my travel map".
        my travel map: This is the fake dataset for a travel foot print log including 4 cities in NY: New York -> Seattle -> Los Angela -> Miami.
        life log: This is the fake dataset contains the daily active routine of a Columbia nerd.
        starbuck: This is the fake dataset contains the starbucks income changed by date around New Haven city and neighorhoods.

    Returns
    ---
    Relative dataframes.

    Example
    ---
    travel = pv.get_demo_data(df, "my travel map")
    life = pv.get_demo_data(df, "life log")
    starb = pv.get_demo_data(df, "starbuck")

    >> travel.columns
    Index(['unique_id', 'spot_name', 'street', 'city', 'state', 'country',
       'interest_value', 'date', 'symbol'],
      dtype='object')

    """
    if demo_data == "my travel map":
        df = df.iloc[
            0:4,
        ]
    elif demo_data == "life log":
        df = df.iloc[
            4:7,
        ]
    elif demo_data == "starbuck":
        df = df.iloc[
            7:,
        ]
    return df
