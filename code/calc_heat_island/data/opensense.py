import json
import zipfile
import numpy as np
import pandas as pd

from pathlib import Path
from datetime import datetime
from osgeo import ogr, gdal, osr

from .db import Database


DB = Database(Path("./opensense/"))


def _add_fields(layer):
    layer.CreateField(ogr.FieldDefn("ID", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Temp", ogr.OFTReal))


def layer_path(when, key, *, extra="", ext="geojson"):
    path = Path(f"./layers/{when.strftime('%Y')}/{when.strftime('%m')}/{when.strftime('%d')}/")
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{key}_{when.strftime('%Y-%m-%d_%H_%M')}{'_' + extra if extra != '' else ''}.{ext}"


def build_layer(key, when: datetime, *, path=None):
    if path is None:
        path = layer_path(when, key)
    driver = ogr.GetDriverByName("GeoJSON")
    data_source = driver.CreateDataSource(str(path.resolve()))

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    layer = data_source.CreateLayer(path.stem, srs, ogr.wkbPoint)
    _add_fields(layer)
    features = DB.features(layer, when)
    i = 0
    for i, feature in enumerate(features):
        layer.CreateFeature(feature)
    assert i > 0, "no data found"
    data_source = None # IMPORTANT


def build_all(key: str):
    global DB
    for when in DB.layers():
        path = layer_path(when, key)
        if path.exists():
            continue
        print(f"Building vector layer for {when.strftime('%Y-%m-%d %H:%M')}...", end="")
        try:
            build_layer(key, when, path=path)
            print("done")
        except AssertionError:
            print("failed")

def init():
    global DB
    DB.load(datetime(year=2019, month=7, day=25), "temperature_hot2019_10min_avg.json")
    DB.load(datetime(year=2020, month=8, day=9), "temperature_hot2020_10min_avg.json")
