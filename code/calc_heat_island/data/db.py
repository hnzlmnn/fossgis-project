import sys
import json
import pandas as pd
import numpy as np
import requests
import urllib

from datetime import datetime, timedelta
from osgeo import ogr

BBOX = [
    13.09,
    52.34,
    13.76,
    52.68,
]

COLUMNS = ["lat", "lon", "height", "boxName", "boxId", "exposure", "unit", "value", "createdAt", "phenomenon", "sensorId", "sensorType"]


class Database:

    def __init__(self, path):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.measurements = {}
        self.stations = {}

    def _full_data(self, measurements, station):
        for stations in measurements.values():
            if station not in stations:
                return False
        return True

    def _filter_std(self, measurements):
        values = np.array(list(measurements.values()))
        mean = np.mean(values)
        std = np.std(values)
        return {k: v for k, v in measurements.items() if abs(v - mean) < 2 * std}

    def _load_file(self, fn, when):
        with open(fn, 'r', encoding="utf8") as f:
            data = json.load(f)
        stations = {}
        measurements = {}
        for station_data in data:
            stations[station_data['sensorId']] = dict(
                lat=station_data['lat'],
                lon=station_data['lon'],
                name=station_data['boxName'],
            )
            if station_data['unit'] != "°C":
                raise ValueError("only degree celsius is supported")
            for key, value in station_data['measurements'].items():
                try:
                    time = datetime.fromisoformat(key)
                except ValueError:
                    continue
                if time.year != when.year or time.month != when.month or time.day != when.day:
                    continue
                measurements.setdefault(time, {})
                measurements[time][station_data['sensorId']] = value
        stations = {k: v for k, v in stations.items() if self._full_data(measurements, k)}
        for time in measurements.keys():
            measurements[time] = {k: v for k, v in measurements[time].items() if k in stations}
            measurements[time] = self._filter_std(measurements[time])
        stations = {k: v for k, v in stations.items() if self._full_data(measurements, k)}
        return stations, measurements

    def download_csv(self, when: datetime, src):
        print(f"Downloading data for {when.strftime('%Y-%m-%d %H:%M')}...", end="", flush=True)
        start = datetime(year=when.year, month=when.month, day=when.day)
        end = start + timedelta(hours=24)
        with requests.get(f"https://api.opensensemap.org/boxes/data", stream=True, params=urllib.parse.urlencode({
            # "boxid": ",".join(BOX_IDS),
            "bbox": ",".join(map(str, BBOX)),
            "columns": ",".join(COLUMNS),
            "download": "true",
            "format": "csv",
            "from-date": start.isoformat() + "Z",
            "to-date": end.isoformat() + "Z",
            "phenomenon": "Temperatur",
        }, safe=':+,-')) as r:
            assert r.status_code == 200, "failed to download the data"
            with open(src, "wb+") as f:
                for chunk in r.iter_content(chunk_size=1024): 
                    f.write(chunk)
        print("done", flush=True)

    def transform_csv(self, when: datetime, dst, *, period: timedelta = None):
        if period is None:
            period = timedelta(minutes=10)
        print(f"Converting data for {when.strftime('%Y-%m-%d %H:%M')}...", end="", flush=True)
        start = datetime(year=when.year, month=when.month, day=when.day)
        end = start + timedelta(hours=24)
        csv_file = (self.path / dst).stem + ".csv"
        df = pd.read_csv(self.path / csv_file, parse_dates=['createdAt'],date_parser=lambda v: datetime.fromisoformat(v[:-1]))

        def create_sensor(df):
            return dict(
                boxName=df.iloc[0]['boxName'],
                boxId=df.iloc[0]['boxId'],
                lon=df.iloc[0]['lon'],
                lat=df.iloc[0]['lat'],
                sensorId=df.iloc[0]['sensorId'],
                unit=df.iloc[0]['unit'],
                measurements={k.isoformat():v['value'] for k,v in df
                    .drop('lat', axis=1)
                    .drop('lon', axis=1)
                    .drop('height', axis=1)
                    .set_index('createdAt')
                    .loc[end.isoformat():start.isoformat()]
                    .resample(period)
                    .mean()
                    .dropna()
                    .to_dict('index')
                    .items()}
                )
        
        df_sensors = df.groupby('sensorId')
            
        with open(self.path / dst, "w+") as f:
            json.dump([
                create_sensor(df_sensors.get_group(x)) for x in df_sensors.groups
            ], f)
        print("done", flush=True)

    def load(self, when, src):
        try:
            if not (self.path / src).exists():
                csv_file = self.path / ((self.path / src).stem + ".csv")
                if not csv_file.exists():
                    self.download_csv(when, csv_file)
                self.transform_csv(when, src)
            print(f"Loading {when.strftime('%Y-%m-%d %H:%M')}...", end="", flush=True)
            stations, measurements = self._load_file(self.path / src, when)
            self.stations.update(stations)
            self.measurements.setdefault(when.year, {})
            self.measurements[when.year].setdefault(when.month, {})
            self.measurements[when.year][when.month].setdefault(when.day, {})
            for when, measurement in measurements.items():
                for sid, value in measurement.items():
                    self.measurements[when.year][when.month][when.day].setdefault(when.hour, {})
                    self.measurements[when.year][when.month][when.day][when.hour].setdefault(when.minute, {})
                    self.measurements[when.year][when.month][when.day][when.hour][when.minute][sid] = value
            print("done")
        except AssertionError:
            print("failed")

    def years(self):
        return self.measurements.keys()

    def months(self, year):
        return self.measurements.get(year, {}).keys()

    def days(self, year, month):
        return self.measurements.get(year, {}).get(month, {}).keys()

    def hours(self, year, month, day):
        return self.measurements.get(year, {}).get(month, {}).get(day, {}).keys()

    def minutes(self, year, month, day, hour):
        return self.measurements.get(year, {}).get(month, {}).get(day, {}).get(hour, {}).keys()

    def values(self, year, month, day, hour, minute):
        return self.measurements.get(year, {}).get(month, {}).get(day, {}).get(hour, {}).get(minute, {})

    def layers(self):
        for year in self.years():
            for month in self.months(year):
                for day in self.days(year, month):
                    for hour in self.hours(year, month, day):
                        for minute in self.minutes(year, month, day, hour):
                            yield datetime(year=year, month=month, day=day, hour=hour, minute=minute)

    def get(self, when: datetime, *, station: int = None):
        stations = self.values(when.year, when.month, when.day, when.hour, when.minute)
        if len(stations) == 0:
            return {}
        if station is None:
            return stations
        if isinstance(station, (list, tuple)):
            return {sid: s for sid, s in stations.items() if sid in station}
        data = stations.get(station, None)
        if data is None:
            return {}
        return {station: data}

    def _to_feature(self, layer, sid, measurement):
        station = self.stations.get(sid, None)
        if station is None:
            return None
        feature = ogr.Feature(layer.GetLayerDefn())
        # Set the attributes using the values from the delimited text file
        feature.SetField("ID", sid)
        feature.SetField("Temp", measurement)
        wkt = "POINT(%f %f)" %  (station['lon'], station['lat'])
        feature.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
        return feature

    def features(self, layer, *args, **kwargs):
        for k, v in self.get(*args, **kwargs).items():
            f = self._to_feature(layer, k, v)
            if f is None:
                continue
            yield f

