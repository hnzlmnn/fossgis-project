import sys
import json
import pandas as pd
import numpy as np
import requests
import urllib

from datetime import datetime, timedelta
from osgeo import ogr

# BOX_IDS = [
#     "53b2ab5de79c90a0102b04ea",
#     "56ded8d82cb6e1e41078f572",
#     "5719c4037514d05c121e317c",
#     "57ff3ab2f1b6070012da9c06",
#     "582473be40198a001010e1a3",
#     "58418d5b5850ba001602063a",
#     "586e95a7896c420011bbb591",
#     "5889cb92ff876d00101be9dd",
#     "58a1dd3d8c2b5000115b409c",
#     "58b4531ee53e0b001251d07b",
#     "58f0cd55ba279000119c3c02",
#     "5908e9935ba9e500113a98d9",
#     "590b8480dd09cc0011aa79cc",
#     "591ecdc251d3460011651ff9",
#     "592c17fd51d3460011e49fce",
#     "592ca4b851d3460011ea2635",
#     "5931701ead0fa30011cc3141",
#     "593458ddad0fa30011ea0961",
#     "593468a5ad0fa30011eaae38",
#     "5936c52aad0fa30011033d67",
#     "593c1eb76ccf3b00117c938f",
#     "594c01c7be77820011792180",
#     "595178fb94f0520011e083ec",
#     "59592d0994f05200114428e8",
#     "59726009fe1c74001138e0cf",
#     "597f4ff4e3b1fa001013c1d7",
#     "5984c712e3b1fa0010691509",
#     "5998a7bad67eb500114b7d76",
#     "599f3364d67eb50011b85cd0",
#     "59a2a715d67eb50011f5a17b",
#     "59b9030bd67eb500117a3fed",
#     "59d10f6f66f66a0010fde34a",
#     "59d7db4666f66a0010793e36",
#     "59e50fb549f6f800112ffcfe",
#     "59f8af62356823000fcc460c",
#     "59fe4c93d13da400100069ad",
#     "59ff7429d13da40010178bab",
#     "5a1185849fd3c200118188af",
#     "5a1c316019991f0011cdd730",
#     "5a414a7cfaf306000fbb6b99",
#     "5a524c69fa02ec000fe2a95c",
#     "5a55cd5a53bf5e00129b68a3",
#     "5a57e3692b734700103d5e59",
#     "5a5ade44999d43001bb1efed",
#     "5a746c9d29b729001acaa18b",
#     "5a77184229b729001a150c10",
#     "5a771c8829b729001a158743",
#     "5a7c6e30398b82001137b271",
#     "5a7f2eb1398b82001189eb65",
#     "5a8813f1bc2d41001988ede6",
#     "5a8c3d36bc2d4100190c49fb",
#     "5a914cfabc2d410019af5758",
#     "5a9f8f48f55bff001a69780a",
#     "5aa68042396417001bcc34ff",
#     "5ab106ce850005001b6d70a3",
#     "5abd607d850005001b23d864",
#     "5ad02a90223bd8001989ff5e",
#     "5aef2c23223bd80019493ebc",
#     "5af4b3c3223bd80019284e95",
#     "5afdcb33223bd8001995fb21",
#     "5b116f734cd32e0019d35cfb",
#     "5b14eda64cd32e00195ec2c8",
#     "5b2972ec1fef04001bf16620",
#     "5b4898475dc1ec001b8e0742",
#     "5b4c88275dc1ec001b3c3bc2",
#     "5b4e37c25dc1ec001b870cb0",
#     "5b5e071441718300198cc5f0",
#     "5b7b3bda2afec7001994f398",
#     "5b859a6f7c519100194ccba6",
#     "5b905c477c519100194292d8",
#     "5b9b909c7c519100194b8a94",
#     "5ba398fde62474001909bac3",
#     "5ba8bffee624740019fa7878",
#     "5bba392b043f3f001b2e5764",
#     "5bba72b1043f3f001b38f1bf",
#     "5bbb1803bc400c001b2fa556",
#     "5bd56bac6a8607001b9bca2b",
#     "5be45027cdfcd0001cde051f",
#     "5bf50e2786a6b500192f8fa2",
#     "5bf8372e86f11b001aae619f",
#     "5bf8373386f11b001aae627e",
#     "5bf8374086f11b001aae64e0",
#     "5bf8374186f11b001aae6548",
#     "5bf8375486f11b001aae682f",
#     "5bf8379b86f11b001aae793f",
#     "5bf8379d86f11b001aae79cf",
#     "5bf837bf86f11b001aae7f82",
#     "5bf8381086f11b001aae8f6a",
#     "5bf93b1ba8af82001afbee7f",
#     "5bf93b47a8af82001afbf69a",
#     "5bf93b63a8af82001afbfbc0",
#     "5bf93bd1a8af82001afc12de",
#     "5bf93be1a8af82001afc1568",
#     "5bf93befa8af82001afc1821",
#     "5bf93bf4a8af82001afc18d0",
#     "5bf93c02a8af82001afc1b98",
#     "5bf93c3fa8af82001afc2a11",
#     "5bf93c41a8af82001afc2a97",
#     "5bf93c58a8af82001afc2e91",
#     "5bf93ceba8af82001afc4c32",
#     "5bf93d3ba8af82001afc5adb",
#     "5bf93d3ba8af82001afc5aeb",
#     "5bf93d42a8af82001afc5bfa",
#     "5bf93d62a8af82001afc650b",
#     "5bf95659a8af82001a01751e",
#     "5bfbbe2ed70bea001a682233",
#     "5c0166eaccc67b001c89e138",
#     "5c01676accc67b001c89f9ef",
#     "5c0167a6ccc67b001c8a07dd",
#     "5c016809ccc67b001c8a1bae",
#     "5c016861ccc67b001c8a2d39",
#     "5c01686bccc67b001c8a2efd",
#     "5c01687fccc67b001c8a325c",
#     "5c016888ccc67b001c8a3465",
#     "5c01688accc67b001c8a351e",
#     "5c0168b3ccc67b001c8a3ffe",
#     "5c0169edccc67b001c8a8117",
#     "5c1d220a919bf8001ad93500",
#     "5c21ff8f919bf8001adf2488",
#     "5c22ef44919bf8001a10acc7",
#     "5c253d5e919bf8001a8b9942",
#     "5c269755919bf8001ad23795",
#     "5c2bca0e2c80100019218e6b",
#     "5c2f48182c80100019e2c2cd",
#     "5c30e2262c80100019368586",
#     "5c32a21b2c8010001993c08e",
#     "5c377effc4c2f3001942a946",
#     "5c4339d41b7ca80019cfb5fe",
#     "5c450f991b7ca800193bfaf0",
#     "5c5d8176c6ca900019c8b200",
#     "5c67ef61a100840019d0afaf",
#     "5c7284849e675600196c6ebf",
#     "5c73c7e79e67560019bfc403",
#     "5c769694973d19001aea4802",
#     "5c7aceaa5094e9001983b731",
#     "5c84ec57922ca900197df105",
#     "5c850a54922ca90019864ed9",
#     "5c8aab08922ca900191ed64d",
#     "5c8d8dc4922ca90019f36238",
#     "5c99233dcbf9ae001adfa984",
#     "5ca4d598cbf9ae001a53051a",
#     "5cacc12c3680f2001b7a20f3",
#     "5cceee2bff898b001a5d420f",
#     "5cd5576eff898b001a1f1d02",
#     "5cd85821ff898b001af92453",
#     "5cd9440aff898b001a3ba6c0",
#     "5ce53c3430705e001aa610d6",
#     "5cecf8f630705e001acb1e3a",
#     "5cf9874107460b001b828c5b",
#     "5cfae181a1ba9f001a19d77b",
#     "5d0600b383fbe0001ad7675e",
#     "5d0bc7eb30bde6001a17e297",
#     "5d0e0ea130bde6001abb3208",
#     "5d0e225130bde6001ac0c459",
#     "5d2818e330bde6001a433828",
#     "5d2f7daf597af3001a63d84a",
#     "5d3edec6953683001abb743a",
#     "5d4e740a953683001a213b8b",
#     "5d5929a0953683001a26e013",
#     "5d5a8d95953683001a8a888c",
#     "5d6be990953683001a7b3bff",
#     "5d6d8d6b953683001af59cdd",
#     "5d6e465a953683001a2b62c5",
#     "5d78d019953683001a3ef921",
#     "5d78d78f953683001a412c1d",
#     "5d7f60d6953683001a27a79a",
#     "5d821912953683001af1f776",
#     "5d8219d2953683001af2303e",
#     "5d8a549d5f3de0001a7c3504",
#     "5d8e1cc45f3de0001a985094",
#     "5d9ef41e25683a001ad916c3",
#     "5d9f216425683a001ae684cb",
#     "5da0a27f25683a001a59271b",
#     "5da202ac25683a001ac232e4",
#     "5dadbbc6203db9001afe59e7",
#     "5dbddb15a68df4001a82fe59",
#     "5dbf1a8ba68df4001adead2e",
#     "5dc5d2d37d4ff7001ac7861f",
#     "5dcbe2d1306947001a2c353b",
#     "5dcc3625306947001a431df3",
#     "5dd810224ec04e001a22129f",
#     "5dd98e596e5e9f001a324e99",
#     "5dda63156e5e9f001a6c8867",
#     "5df0c3702b3516001a4efb2e",
#     "5df0c3bc2b3516001a4f139a",
#     "5df0c60d2b3516001a4fc833",
#     "5df0c67b2b3516001a4fe5db",
#     "5df0c7842b3516001a5036af",
#     "5df0e0a22b3516001a57b511",
#     "5df0e14a2b3516001a57eb1d",
#     "5df0e22a2b3516001a582a53",
#     "5e0089a35b8d95001a868e0b",
#     "5e02b67d475fc6001a132e31",
#     "5e07550d8c8053001a9fe665",
#     "5e078ec58c8053001ab1950d",
#     "5e0880f28c8053001afb27b6",
#     "5e0ba32b7c9a10001ac5ca65",
#     "5e120d9cb0c088001b561a79",
#     "5e127d1fe5e60c001a89aba0",
#     "5e14e11ae5e60c001a4e572d",
#     "5e1f4b56b459b2001eed0f57",
#     "5e22d7a87993c4001bfb1f5d",
#     "5e25fe07386af6001a5771b4",
#     "5e26d166386af6001aa115db",
#     "5e40394f72fd16001b5db424",
#     "5e47fbc837d527001b6845fe",
#     "5e4b87f099046c001cda06c0",
#     "5e4bf982efa9e4001b6acc03",
#     "5e5a982be8fdda001bf77e88",
#     "5e5e44d657703e001bf30c5b",
#     "5e5fc72957703e001b7b1f0a",
#     "5e60cf5557703e001bdae7f8",
#     "5e6defe2ee48fc001dffc47b",
#     "5e78a4a92b36bf001c58e41a",
#     "5e8204635c2147001bed3c53",
#     "5e899b826feb97001c67d63a",
#     "5e8f8d09df8258001bbb8787",
#     "5e94612cdf8258001b804ef3",
#     "5e962b0dafee03001ba22a8e",
#     "5e98cc6045f937001c0e7c53",
#     "5e9af8d545f937001ce58076",
#     "5e9c402a45f937001c65b6e5",
#     "5e9d8d9545f937001ce9352a",
#     "5ea150b5742006001bff5239",
#     "5ea45ff9c2c39c001c5be103",
#     "5ead8dfe712645001bb2fea3",
#     "5eb174ef9724e9001cf3592d",
#     "5eb1a8d39724e9001c07e23a",
#     "5eb3ca239724e9001ce38a9f",
#     "5eb3d22a9724e9001ce6d240",
#     "5eb99cacd46fb8001b2ce04c",
#     "5eba5fbad46fb8001b799786",
#     "5ebc0c99d46fb8001b2182b0",
#     "5ec950aed0545b001ca9a93e",
#     "5ed769a8d0545b001c4b60ab",
#     "5ed76a4bd0545b001c4b9fe2",
#     "5ed76b35d0545b001c4bf92a",
#     "5ee09fc394874a001d2bb72e",
#     "5ee30038dc1438001bda33fb",
#     "5ee354e7dc1438001bfb75bd",
#     "5ee35586dc1438001bfbb7b3",
#     "5ee5041cdc1438001ba74ed5",
#     "5ee68c06dc1438001b43349f",
#     "5eeb4365ee9b25001b139de7",
#     "5ef34c16ee9b25001b5a5e99",
#     "5ef9e648792d6f001bad670c",
#     "5eff2c83b9d0aa001c082e42",
#     "5f0c6be8987fd4001b9eba22",
#     "5f19eada586e36001c8ecdd5",
#     "5f1ad789586e36001cf1f602",
#     "5f1eda639fc38a001ba99e1d",
#     "5f22b5393f5e46001b60ffa5",
#     "5f2ab2c8263635001cdba927",
#     "5f4243f4214b72001cd27833",
#     "5f53fb3a37e925001b6592eb",
#     "5f5c9b7184e5a2001ba365e9",
#     "5f6b0d50dc5cc6001bef7d58",
#     "5f7372f2821102001ba0ed95",
#     "5f745eb5821102001b03fc8b",
#     "5f7842a5e6255b001b2f12dd",
#     "5f8489a5a1fdbf001b2618a5",
#     "5f85da96b0cbe8001beb93a6",
#     "5f88ceb10511d8001cd3f59b",
#     "5f8d7aa036d43d001c1df37a",
#     "5f975daf321dc8001bba519d",
#     "5fa5cae667d8a1001b1e3fe6",
#     "5fad60d49b2df8001b04ec23",
#     "5fb7de317a70a5001c6af2da",
#     "5fbfb94deb7b78001cfccb77",
#     "5fc390363a7437001b622d33",
#     "5fc4fc25c949b9001b158782",
#     "5fc5034ac949b9001b18c241",
#     "5fcc05a9fab469001c59ebd8",
#     "5fce3658fab469001c594e7d",
#     "5fd21f6d44fb1e001cded7e7",
#     "5fd3def2e55e0e001bbd827a",
#     "5fe5b0c7c31ca0001c53b9ca",
#     "5fea3f08576ab7001c00d149",
#     "5ff08241338b08001b2b1608"
# ]
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
            # measurements[time] = filter_std(measurements[time])
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

