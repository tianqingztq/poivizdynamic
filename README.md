# poivizdynamic

Animate your point-of-interest map! Make the point-trace/ value-trend moving! 

This package helps users more easily visualize dynamic points/ value change on the map, observing {value amount/ point position} changes dynamically as the time-bar moves forward. 

Users firstly need to prepare the POI dataset following the fake_demo_data format which can be found in the poivizdynamic/data folder. Then they can customize their easy animated maps with functions provided here.

## Installation

Please install and import the censusviz package using the following commands.

```bash
$ pip install poivizdynamic
```
or

```bash
$ pip install -i https://test.pypi.org/simple/ poivizdynamic
```

After installing via pip, please import the package to use on your Python IDE.

```bash
from poivizdynamic import poivizdynamic as pv
```

## Usage

### Prepare Correct Format of Data in Interests

The input csv data should contains the following information (columns):
basic info:
- unique_id: the unique id of the POIs
- spot_name: the name of the POIs	(i.e. Popeyes)
address info:
- street: correct street information of the POIs (i.e. 321 W 125th St)
- city: the city info of the POIs	(i.e.  New York/ NY)
- state: the state info of the POIs   (i.e.  New York/ NY)
- country: the country info of the POIs	
value of interests:
- interest_value: if interest in point move, just leave this blank or 0; 
        if interested in value change, fill it here!
time series info:
- date
icon of POI:
- symbol: choose your icon for your POIs (i.e. airport, rail, car, airport, library, lodging, fast-food)
        more icons' name info can be found here: https://labs.mapbox.com/maki-icons/

The sample csv file "fake_demo_data.csv" can be found in the poivizdynamic/data folder. 

```bash
df = pd.read_csv(<your own data here>)

# demo_data
df = pd.read_csv('.src/poivizdynamic/data/demo_fake_data.csv')
```

### Return a 

```bash
# demo_data
travel = pv.get_demo_data(df, "my travel map")
travel = pv.get_geo_dataset(api_key_w, travel)  # default maptype is world
travel = pv.clean_dataset(travel)
```



```bash
# footprint map
pv.get_footprint_map(TOKEN_MAPBOX, travel, fig_name = "my foot print", title_text = "My Animated Footprint Map")
```
Get a screenshot of the dynamic result!

![](demo_output/footprint_static.png)


```bash
# load and prepare the "life" demo data 
life = pv.get_geo_dataset(api_key_w, life)
life = pv.clean_dataset(life)

# footprint map
pv.get_footprint_map(TOKEN_MAPBOX, life, zoom = 14.5, title_text = "My Daily Life", fig_name = "life")
```

![](demo_output/life_static.png)


```bash
# load and prepare the "starbuck" demo data 
starb2 = pv.get_geo_dataset(api_key_us, starb, maptype = "US")
starb2 = pv.clean_dataset(starb2)

# bubble map with color_group_lab = YOUR_INTEREST_VALUE
pv.get_animated_bubble_map(TOKEN_MAPBOX, starb2, zoom = 10, color_value_discrete = False, bubble_size = "interest_value", color_group_lab = "interest_value", fig_name = "starbuck2")
```
![](demo_output/starbuck2_static.png)


```bash
# bubble map with color_group_lab = POI'S NAME
pv.get_animated_bubble_map(TOKEN_MAPBOX, starb2, zoom = 10, color_value_discrete = False, bubble_size = "interest_value", color_group_lab = "spot_name", fig_name = "starbuck1")
```
![](demo_output/starbuck1_static.png)



#### Detailed Help Document When Using the Functions

Access to the help document using the following lines.

```bash
?pv.get_coordinate_api
?pv.get_geo_dataset
?pv.clean_dataset

?pv.get_footprint_map
?pv.get_animated_bubble_map

?pv.get_demo_data
```









## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## Dependencies

- python = "^3.9"
- pandas = "^1.3.5"
- plotly = "^5.4.0"
- requests = "^2.26.0"
- timer = "^0.2.2"
- datetime = "^4.3"

## Documentation

The unofficial documentation can be found under this relative path: .docs/_build/html/index.html

## License

`poivizdynamic` was created by TianqingZhou. It is licensed under the terms of the MIT license.

## Credits

`poivizdynamic` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
