import argparse

from pathlib import Path
from osgeo import gdal

ALGORITHMS = {
    "invdistnn": "gdal",
    "linear": "gdal",
    "nearest": "gdal",
    "spline": "TODO",
}

config = dict(
    radius=1.0,
    power=2.0,
    smoothing=0.0,
    neighbors=12,
)

BBOX = [
    13.09,
    52.34,
    13.76,
    52.68,
]

parser = argparse.ArgumentParser(prog="Interpolation Demo", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-a", "--algo", dest="algo", type=str, default=list(ALGORITHMS.keys())[0], choices=list(ALGORITHMS.keys()), help="Select an interpolation algorithm")
parser.add_argument("INPUT", nargs=1, help="The input file to interpolate on (GeoJSON)")

args = parser.parse_args()

if args.algo == "linear":
    conf = f"linear:radius={config['radius']}"
elif args.algo == "invdistnn":
    conf = f"invdistnn:power={config['power']}:smoothing={config['smoothing']}:radius={config['radius']}:max_points={config['neighbors']}:min_points=0"
elif args.algo == "nearest":
    conf = f"nearest"
elif args.algo == "spline":
    conf = ""

gis = ALGORITHMS[args.algo]

#print(args)

src = Path(args.INPUT[0])

dst = src.parent / f"{src.stem}_{args.algo}.tiff"

if gis == "gdal":
    result = gdal.Grid(
        str(dst.resolve()),
        str(src.resolve()),
        format="GTiff",
        outputBounds=BBOX,
        width=1024, height=1024,
        outputType=gdal.GDT_Float32,
        algorithm=conf,
        zfield="Temp",
    )
    result = None
elif gis == "":
    pass

