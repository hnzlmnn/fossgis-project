import sys
import pickle


class Database:

    def __init__(self, path, load_entries=False):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.entries = {}
        self.data = {}

    @property
    def entries_file(self):
        return self.path / "entries.pickle"

    def load_entries(self):
        if not self.entries_file.exists():
            return False
        with open(self.entries_file, "rb") as f:
            for year, month, days in pickle.load(f):
                self.entries.setdefault(year, {})
                self.entries[year].setdefault(month, {})
                for day, hours in days:
                    self.entries[year][month][day] = hours
        return True

    def add_measurement(self, date, sid, measurement):
        if measurement["TT_TU"] == -999:
            # Skip missing values
            return
        self.data.setdefault(date.year, {})
        self.data[date.year].setdefault(date.month, {})
        self.data[date.year][date.month].setdefault(date.day, {})
        self.data[date.year][date.month][date.day].setdefault(date.hour, {})
        self.data[date.year][date.month][date.day][date.hour][sid] = measurement

    def load_month(self, year, month):
        print(f"Loading {year}-{('0' * 2 + str(month))[-2:]}...", end="")
        sys.stdout.flush()
        with open(self.path / f"{year}_{month}.pickle", "rb") as f:
            days =  pickle.load(f)
            self.data.setdefault(year, {})
            self.data[year].setdefault(month, {})
            self.data[year][month] =  days
        print("done")

    def save(self):
        entries = []
        for year, months in self.data.items():
            for month, days in months.items():
                measurements = sum(len(hours) for hours in days.values())
                if measurements == 0:
                    continue
                with open(self.path / f"{year}_{month}.pickle", "wb+") as f:
                    pickle.dump(days, f)
                entries.append((year, month, [(day, list(hours.keys())) for day, hours in days.items()]))
        with open(self.entries_file, "wb+") as f:
            pickle.dump(entries, f)

    def years(self):
        return self.entries.keys()

    def months(self, year):
        return self.entries.get(year, {}).keys()

    def days(self, year, month):
        return self.entries.get(year, {}).get(month, {}).keys()

    def hours(self, year, month, day):
        return self.data.get(year, {}).get(month, {}).get(day, [])

    def layers(self):
        for year in self.years():
            for month in self.months(year):
                for day in self.days(year, month):
                    for hour in self.hours(year, month, day):
                        yield year, month, day, hour


    def is_loaded(self, year, month):
        return self.data.get(year, {}).get(month, None) is not None

    def get(self, year: int, month: int, day: int, hour: int, station: int = None):
        if not self.is_loaded(year, month):
            self.load_month(year, month)
        stations = self.data.get(year, {}).get(month, {}).get(day, {}).get(hour, {})
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

