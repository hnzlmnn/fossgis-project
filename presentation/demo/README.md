# FOSSGIS Seminar WS20/21 Interpolation Demo
## Setup
The program requires Python3 with the GDAL module available.
### Windows
We recommend using [OSGeo4W](https://www.osgeo.org/projects/osgeo4w/) and then activating the python 3 environment within the OSGeo4W Shell using `py3_env`.
### Linux/Mac
Although not tested you should be able to install GDAL through [pip](https://pypi.org/project/GDAL/). As the program requires Python3, make sure to install the pacakge for Python3 and not Python2.
## Instructions
Use `demo.py --help` to list available options.
### Windows
For Windows please activate `py3_env` in your OSGeo4W shell before running the demo.
## Expected Result
The program creates the interpolation with the selected input file and algorithm. Open the generated GeoTiff in e.g. QGis to colorize and overlay with the measurement stations the input file.