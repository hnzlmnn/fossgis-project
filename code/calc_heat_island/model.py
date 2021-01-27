import geojson
import gdal_calc
import time
import json
import rasterio
import numpy as np

import calc_heat_island.data

from geojson import Feature, FeatureCollection, Point
from osgeo import gdal, ogr
from datetime import datetime
from calc_heat_island.data import DB, layer_path, build_layer, BBOX
from .colorize import colorize
from .util import QUALITIES
from .frame import store_frame_txt, build_frame, build_animation


ALGORITHMS = [
    "invdistnn",
    "linear",
    "nearest",
]


def algo_config(algo: str, **kwargs):
    if algo == "invdistnn":
        return f"invdistnn:power={kwargs['power']}:smoothing={kwargs['smoothing']}:radius={kwargs['radius']}:max_points={kwargs['neighbors']}:min_points=0"
    if algo == "linear":
        return f"linear:radius={kwargs['radius']}"
    raise ValueError("invalid algo selected: " + algo)


def calc_layer(algo: str, key: str, year: int, month: int, day: int, hour: int, minute: int, *, power: float = 2.0, smoothing: float = 0.0, radius: float = 1.0, neighbors: int = 12, quality: int, **kwargs):
    if not (isinstance(year, int) and isinstance(month, int) and isinstance(day, int) and isinstance(hour, int)):
        raise ValueError("Invalid time!")
    when = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    src_path = layer_path(when, key)
    if not src_path.exists():
        build_layer(key, when, path=src_path)
    tmp_path = layer_path(when, key, algo=algo, extra="temp", ext="tiff")
    if tmp_path.exists():
        return
    print(f"Calculating layer for {when.strftime('%Y-%m-%d %H:%M')}...", end="", flush=True)
    result = gdal.Grid(
        str(tmp_path.resolve()),
        str(src_path.resolve()),
        format="GTiff",
        outputBounds=BBOX,
        width=QUALITIES[quality][0], height=QUALITIES[quality][1],
        outputType=gdal.GDT_Float32,
        algorithm=algo_config(algo, power=power, smoothing=smoothing, radius=radius, neighbors=neighbors),
        zfield="Temp",
    )
    result = None

    img = rasterio.open(tmp_path)

    ch = img.read(1)
    extrema = (float(np.min(ch)), float(np.max(ch)))
    extrema_file = tmp_path.parent / f"{key}_{algo}_extrema.json"
    global_extrema = {}
    if extrema_file.exists():
        with open(extrema_file, "r") as fin:
            global_extrema = json.load(fin)
    global_extrema[when.strftime('%Y-%m-%d %H:%M')] = extrema
    with open(extrema_file, "w+") as fout:
        json.dump(global_extrema, fout)
    print("done", flush=True)


def process_layer(algo: str, key: str, year: int, month: int, day: int, hour: int, minute: int, *, srs: str, quality: int, **kwargs):
    if not (isinstance(year, int) and isinstance(month, int) and isinstance(day, int) and isinstance(hour, int)):
        raise ValueError("Invalid time!")
    when = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    tmp_path = layer_path(when, key, algo=algo, extra="temp", ext="tiff")
    color_path = layer_path(when, key, algo=algo, extra="color", ext="tiff")
    if color_path.exists():
        color_path.unlink()
    dst_path = layer_path(when, key, algo=algo, ext="tiff")
    if dst_path.exists():
        dst_path.unlink()
    frame_path = layer_path(when, key, algo=algo, ext="png")
    if frame_path.exists():
        store_frame_txt(algo, key, frame_path)
        return
    print(f"Processing image for {when.strftime('%Y-%m-%d %H:%M')}...", end="", flush=True)
    if not tmp_path.exists():
        raise ValueError(f"The layer for {when.strftime('%Y-%m-%d %H:%M')} needs to be calculated first!")
    
    img = rasterio.open(tmp_path)
    meta = img.meta
    meta.update(dict(
        count=4,
        dtype='uint8',
    ))
    ch = img.read(1)

    extrema_file = tmp_path.parent / f"{key}_{algo}_extrema.json"
    global_extrema = {}
    if extrema_file.exists():
        with open(extrema_file, "r") as fin:
            global_extrema = json.load(fin)
    extrema = [255, -255]
    for local_extrema in global_extrema.values():
        extrema[0] = min(extrema[0], local_extrema[0])
        extrema[1] = max(extrema[1], local_extrema[1])

    r, g, b, a = colorize(ch, extrema)
    with rasterio.open(
        color_path,
        'w',
        **meta,
    ) as dst:
        dst.write(r, 1)
        dst.write(g, 2)
        dst.write(b, 3)
        dst.write(a, 4)

    result = gdal.Warp(
        str(dst_path.resolve()),
        str(color_path.resolve()),
        dstSRS=srs,
        cropToCutline=True,
        cutlineDSName="util/berlin.geojson",
    )
    result = None

    build_frame(dst_path, when, frame_path, extrema=extrema, quality=quality)
    print("done", flush=True)


def process_single(algo: str, key: str, year: int, month: int, day: int, hour: int, minute: int, **kwargs):
    when = datetime(year=year, month=month, day=day)
    extrema_file = layer_path(when, key, algo=algo, extra="temp", ext="tiff").parent / f"{key}_{algo}_extrema.json"
    extrema = {}
    if extrema_file.exists():
        with open(extrema_file, "r") as fin:
            extrema = json.load(fin)
    for check_hour in DB.hours(year, month, day):
        for check_minute in DB.minutes(year, month, day, check_hour):
            when = datetime(year=year, month=month, day=day, hour=check_hour, minute=check_minute)
            if not when.strftime('%Y-%m-%d %H:%M') in extrema.keys():
                return
    process_layer(algo, key, year, month, day, hour, minute, **kwargs)


def calc_hour(algo: str, key: str, year: int, month: int, day: int, hour: int, **kwargs):
    for minute in DB.minutes(year, month, day, hour):
        calc_layer(algo, key, year, month, day, hour, minute, **kwargs)


def process_hour(algo: str, key: str, year: int, month: int, day: int, hour: int, **kwargs):
    for minute in DB.minutes(year, month, day, hour):
        process_layer(algo, key, year, month, day, hour, minute, **kwargs)


def calc_day(algo: str, key: str, year: int, month: int, day: int, **kwargs):
    for hour in DB.hours(year, month, day):
        calc_hour(algo, key, year, month, day, hour, **kwargs)
    process_day(algo, key, year, month, day, **kwargs)
    build_animation(key, datetime(year=year, month=month, day=day), **kwargs)


def process_day(algo: str, key: str, year: int, month: int, day: int, **kwargs):
    for hour in DB.hours(year, month, day):
        process_hour(algo, key, year, month, day, hour, **kwargs)


def calc_month(algo: str, key: str, year: int, month: int, **kwargs):
    for day in DB.days(year, month):
        calc_day(algo, key, year, month, day, **kwargs)


def calc_year(algo: str, key: str, year: int, **kwargs):
    for month in DB.months(year):
        calc_month(algo, key, year, month, **kwargs)


def calc_all(algo: str, key: str, **kwargs):
    for year in DB.years():
        calc_year(algo, key, year, **kwargs)


def main(key: str, year, month, day, hour, minute, *, algo: str, all: bool, **kwargs):
    calc_heat_island.data.init()
    calc_heat_island.data.build_all(key)
    if year is None:
        # all
        if not all:
            raise RuntimeError("To calculate all layers, 'all' must be set")
        calc_all(algo, key, **kwargs)
    elif month is None:
        # year
        calc_year(algo, key, year, **kwargs)
    elif day is None:
        # month
        calc_month(algo, key, year, month, **kwargs)
    elif hour is None:
        # day
        calc_day(algo, key, year, month, day, **kwargs)
    elif minute is None:
        # day
        calc_hour(algo, key, year, month, day, hour, **kwargs)
    else:
        # single
        calc_layer(algo, key, year, month, day, hour, minute, **kwargs)
        process_single(algo, key, year, month, day, hour, minute, **kwargs)


