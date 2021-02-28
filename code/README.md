# Code
## Setup
The program requires Python3 with the GDAL module available.
### Windows
We recommend using [OSGeo4W](https://www.osgeo.org/projects/osgeo4w/) and then activating the python 3 environment within the OSGeo4W Shell using `py3_env`.
### Linux/Mac
Although not tested you should be able to install GDAL through [pip](https://pypi.org/project/GDAL/). As the program requires Python3, make sure to install the pacakge for Python3 and not Python2.
## Requirements
TODO
### Background map
`background.tiff` as `GeoTiff` that uses the bounding box defined in `util/clipping_boundary.geojson`. The provided `background.qgz` may be used.

The OpenStreetMap data required by `background.qgz` can be obtaind at [Geofabrik](http://download.geofabrik.de/europe/germany/berlin-latest-free.shp.zip)

## TODO

- Add *nix run script.
  - For now manually running `python -m calc_heat_island` should work if the python environment is set-up correctly.
- Create pipenv file for extra dependencies.

