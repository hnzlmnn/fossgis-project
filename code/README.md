# Code

## Requirements

### Background map
`background.tiff` as `GeoTiff` that uses the bounding box defined in `util/clipping_boundary.geojson`. The provided `background.qgz` may be used.

The configurations for the GeoPackages loaded by `background.qgz` for the HOTOSM Export Tool are provided as yaml files in `utils/`.

## TODO

- Add *nix run script.
  - For now manually running `python -m calc_heat_island` should work if the python environment is set-up correctly.
- Create pipenv file for extra dependencies.

