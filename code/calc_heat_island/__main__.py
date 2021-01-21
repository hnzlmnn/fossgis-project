import os
import argparse
import geojson
import calc_heat_island

from pathlib import Path
from datetime import datetime
from calc_heat_island import main, QUALITIES, ALGORITHMS
from osgeo import gdal


parser = argparse.ArgumentParser(prog="Heat Island Interpolation", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# subparsers = parser.add_subparsers(dest="action", required=True)

# Subparsers
# dtm_parser = subparsers.add_parser("dtm")
# model_parser = subparsers.add_parser("model")

# DTM options
# dtm_parser.add_argument("input")
# dtm_parser.add_argument("--resolution", "--res", "-r", default=200, type=int, help="Spatial resolution in meters")
# dtm_parser.add_argument("--srs", "-s", default="EPSG:25832", help="SRS of the DTM")
# dtm_parser.add_argument("-f", "--force", default=False, const=True, action="store_const")

# Model options
parser.add_argument("year", type=int, nargs="?", default=None)
parser.add_argument("month", type=int, nargs="?", default=None)
parser.add_argument("day", type=int, nargs="?", default=None)
parser.add_argument("hour", type=int, nargs="?", default=None)
parser.add_argument("minute", type=int, nargs="?", default=None)
parser.add_argument("--srs", default="EPSG:3395", help="Output srs of rendered images")
parser.add_argument("--all", action='store_const', const=True, default=False)
parser.add_argument("--quality", type=int, default=2, choices=list(range(len(QUALITIES))), help="Depending on the quality you choose, calculation will be faster/slower")
parser.add_argument("--key", type=str, default="hot")
parser.add_argument("--ffmpeg", type=str, default="ffmpeg")
parser.add_argument("--algo", type=str, default=ALGORITHMS[0], choices=ALGORITHMS)

args = parser.parse_args()

# if args.action == "dtm":
#     src = Path(args.input)
#     dst = src.parent / (src.stem + ".tiff")
#     if dst.exists() and not args.force:
#         raise RuntimeError("Output file exists, set force to overwrite")
#     vrt = src.parent / (src.stem + ".vrt")
#     with open(vrt, "w+") as f:
#         f.write(f"""<OGRVRTDataSource>
#     <OGRVRTLayer name="dgm">
#         <SrcDataSource>{src.resolve()}</SrcDataSource>
#         <GeometryType>wkbPoint</GeometryType>
#         <LayerSRS>{args.srs}</LayerSRS>
#         <GeometryField encoding="PointFromColumns" x="field_1" y="field_2" z="field_3" />
#     </OGRVRTLayer>
# </OGRVRTDataSource>""")
#     gdal.Rasterize(
#         str(dst.resolve()),
#         str(vrt.resolve()),
#         attribute="field_3",
#         xRes=args.resolution,
#         yRes=args.resolution,
#     )
# elif args.action == "model":


main(args.key, args.year, args.month, args.day, args.hour, args.minute, algo=args.algo, all=args.all, srs=args.srs, quality=args.quality, ffmpeg=args.ffmpeg)

# calc_heat_island.data.os_extract(Path("opensense/2021-01-01/"))



# for k, v in os.environ.items():
#     print(k, v)

# gdal_rasterize -a field_3 -tr ' + inputRes + ' ' + inputRes + ' xyz_dgm_reader.vrt ' + fileName + '.tif

