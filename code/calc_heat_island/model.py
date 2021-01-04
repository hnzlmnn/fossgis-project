import geojson
import gdal_calc
import time

import calc_heat_island.data

from geojson import Feature, FeatureCollection, Point
from osgeo import gdal, ogr
from datetime import datetime
from calc_heat_island.data import DATES, layer_path, build_layer




def calc_layer(year: int, month: int, day: int, hour: int, *, power: float = 2.0, smoothing: float = 1.0, radius: float = 1.0, neighbors: int = 12):
    print(f"Calculating layer for {datetime(year, month, day, hour).strftime('%Y-%m-%d %H:00')}...", end="", flush=True)
    if not (isinstance(year, int) and isinstance(month, int) and isinstance(day, int) and isinstance(hour, int)):
        raise ValueError("Invalid time!")
    src_path = layer_path(year, month, day, hour)
    if not src_path.exists():
        build_layer(year, month, day, hour, path=src_path)
    tmp_path = dst_path = layer_path(year, month, day, hour, temp=True, ext="tiff")
    if tmp_path.exists():
        tmp_path.unlink()
    dst_path = layer_path(year, month, day, hour, ext="tiff")
    if dst_path.exists():
        return
    result = gdal.Grid(str(tmp_path.resolve()), str(src_path.resolve()),
        format="GTiff",
        # outputBounds=[0.0, 0.0, 100.0, 100.0],
        width=3211, height=4331,
        outputType=gdal.GDT_Float32,
        algorithm=f"invdist:power={power}:smoothing={smoothing}:radius={radius}:max_points={neighbors}",
        zfield="Temp")
    result = None
    gdal_calc.Calc(
        "A - (B / 100.0 * 0.65)",
        A=str(tmp_path.resolve()),
        A_band=1,
        B="data/dgm200.tif",
        B_band=1,
        format="GTiff",
        outfile=str(dst_path.resolve()),
        quiet=True)
    print("done")


def calc_day(year: int, month: int, day: int, **kwargs):
    for hour in DATES.hours(year, month, day):
        calc_layer(year, month, day, hour, **kwargs)


def calc_month(year: int, month: int, **kwargs):
    for day in DATES.days(year, month):
        calc_day(year, month, day, **kwargs)


def calc_year(year: int, **kwargs):
    for month in DATES.months(year):
        calc_month(year, month, **kwargs)


def calc_all(**kwargs):
    for year in DATES.years():
        calc_year(year, **kwargs)


def main(year, month, day, hour, *, all: bool):
    calc_heat_island.data.init()
    calc_heat_island.data.build_all()
    if year is None:
        # all
        if not all:
            raise RuntimeError("To calculate all layers, 'all' must be set")
        calc_all()
    elif month is None:
        # year
        calc_year(year)
    elif day is None:
        # month
        calc_month(year, month)
    elif hour is None:
        # day
        calc_day(year, month, day)
    else:
        # single
        calc_layer(year, month, day, hour)


