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

Access to the help document using the following lines.

```bash
?pv.get_coordinate_api
?pv.get_geo_dataset
?pv.clean_dataset

?pv.get_footprint_map
?pv.get_animated_bubble_map

?pv.get_demo_data
```

![](demo_output/footprint_static.png)

![](demo_output/life_static.png)



![](demo_output/starbuck1_static.png)




![](demo_output/starbuck2_static.png)



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
