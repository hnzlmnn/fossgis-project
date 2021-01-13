import re
import io
import sys
import requests
import zipfile
import pandas as pd
import geojson
import pickle

from pathlib import Path
from datetime import datetime
from osgeo import ogr, gdal, osr
from ..normalize import normalize_temp
from .db import Database


BASE = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/"
REGEX_STATION = r"([0-9]+) +([0-9]+) +([0-9]+) +([0-9]+) +([0-9]+\.[0-9]+) +([0-9]+\.[0-9]+) +((?:[^\s]+ ?)+)\s{2,}((?:[^\s]+ ?)+)"


def _line2data(line):
    match = re.match(REGEX_STATION, line)
    if match is None:
        return None
    return [
        int(match.group(1)),
        datetime.strptime(match.group(2).strip(), '%Y%m%d'),
        datetime.strptime(match.group(3).strip(), '%Y%m%d'),
        int(match.group(4)),
        float(match.group(5)),
        float(match.group(6)),
        match.group(7).strip(),
        match.group(8).strip(),
    ]


def _download_stations(url):
    data = requests.get(BASE + url + "TU_Stundenwerte_Beschreibung_Stationen.txt").content.decode("iso8859-15")
    lines = data.split("\n")[2:]
    df = pd.DataFrame.from_records(
        list(filter(lambda d: d is not None, map(_line2data, lines))),
        index="STATIONS_ID",
        columns=["STATIONS_ID", "von", "bis", "height", "lat", "lon", "name", "bundesland"],
    )
    return df


def _download_station_data(url, i):
    id_str = ("0" * 5 + str(i))[-5:]
    r = requests.get(BASE + url + f"stundenwerte_TU_{id_str}_akt.zip")
    assert r.status_code == 200, "error downloading data"
    content = io.BytesIO(r.content)
    zf = zipfile.ZipFile(content)
    for fn in zf.namelist():
        if fn.startswith("produkt_"):
            break
        fn = None
    assert fn is not None, "no data file found"
    with zf.open(fn, "r") as csv_file:
        return pd.read_csv(csv_file, sep=";", index_col="STATIONS_ID", converters={
            0: lambda d: int(d),
            1: lambda d: datetime.strptime(d, '%Y%m%d%H'),
            2: lambda d: int(d),
            3: lambda d: float(d),
            4: lambda d: float(d),
        })


STATIONS = None
STATIONS_GEO = None
DATES = None
ENTRIES = {}


def init():
    global STATIONS, STATIONS_GEO, DATES, ENTRIES
    print("Initializing...", end="", flush=True)
    url = "climate/hourly/air_temperature/recent/"
    path = Path("./data/")
    path.mkdir(parents=True, exist_ok=True)
    stations_file = path / "stations.pickle"
    if not stations_file.exists():
        stations = _download_stations(url)
        stations.to_pickle(stations_file)
    else:
        stations = pd.read_pickle(stations_file)
    STATIONS = stations
    print("done")
    print("Initializing database...", end="", flush=True)
    DATES = Database(path)
    empty = not DATES.load_entries()
    print("done")
    if empty:
        for sid, _ in stations.iterrows():
            print(f"Downloading measurements for {sid}...", end="", flush=True)
            try:
                data = _download_station_data(url, sid)
                for measurement in data.itertuples():
                    DATES.add_measurement(measurement.MESS_DATUM, sid, measurement._asdict())
                print("done")
            except AssertionError:
                print("failed")
                continue
        print("Storing measurements...", end="")
        sys.stdout.flush()
        DATES.save()
        print("done")

def _add_fields(layer):
    layer.CreateField(ogr.FieldDefn("ID", ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("Temp", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Height", ogr.OFTInteger))


def _vector_feature(layer, sid, measurement):
    station = STATIONS.loc[sid]
    # TODO: Abort on missing
    feature = ogr.Feature(layer.GetLayerDefn())
    # Set the attributes using the values from the delimited text file
    feature.SetField("ID", int(sid))
    feature.SetField("Temp", normalize_temp(measurement["TT_TU"], station.height))
    feature.SetField("Height", int(station.height))
    wkt = "POINT(%f %f %f)" %  (station.lon, station.lat, station.height)
    feature.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
    return feature


def _vector_add_feature(layer, sid, measurement):
    feature = _vector_feature(layer, sid, measurement)
    if feature is None:
        return
    layer.CreateFeature(feature)
    feature = None


def layer_path(year: int, month: int, day: int, hour: int, *, temp=False, ext="geojson"):
    when = datetime(year=year, month=month, day=day, hour=hour)
    path = Path(f"./layers/{when.strftime('%Y')}/{when.strftime('%m')}/{when.strftime('%d')}/")
    path.mkdir(parents=True, exist_ok=True)
    return path / f"data_{when.strftime('%Y-%m-%d_%H')}{'_temp' if temp else ''}.{ext}"


def build_layer(year: int, month: int, day: int, hour: int, station: int = None, *, path=None):
    global DATES
    if path is None:
        path = layer_path(year, month, day, hour)
    data = DATES.get(year, month, day, hour, station)
    assert len(data) > 0, "no data found"
    driver = ogr.GetDriverByName("GeoJSON")
    data_source = driver.CreateDataSource(str(path.resolve()))

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    layer = data_source.CreateLayer(path.stem, srs, ogr.wkbPoint)
    _add_fields(layer)

    for sid, measurement in data.items():
        _vector_add_feature(layer, sid, measurement)
    data_source = None


def build_all():
    global DATES
    for year, month, day, hour in DATES.layers():
        path = layer_path(year, month, day, hour)
        if path.exists():
            continue
        print(f"Building vector layer for {datetime(year, month, day, hour).strftime('%Y-%m-%d %H:00')}...", end="")
        try:
            build_layer(year, month, day, hour, path=path)
            print("done")
        except AssertionError:
            print("failed")