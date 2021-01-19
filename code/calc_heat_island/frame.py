import subprocess

from PIL import Image, ImageFont, ImageDraw
from datetime import datetime

from calc_heat_island.data import layer_path
from .util import QUALITIES


BACKGROUND = None
SCALE = None

def store_frame_txt(key: str, frame_path):
    txt = frame_path.parent / f"{key}_frames.txt"
    frames = []
    try:
        with open(txt, "r") as fin:
            frames = [line.strip("\n") for line in fin.readlines()]
    except FileNotFoundError:
        pass
    frames.append("file " + frame_path.name)
    frames = sorted(set(frames))
    with open(txt, "w+") as fout:
        for frame in frames:
            fout.write(frame)
            fout.write("\n")

def build_frame(src, when, dst, *, extrema, quality):
    global BACKGROUND
    global SCALE
    if BACKGROUND is None:
        BACKGROUND = Image.open("util/background.tiff").resize(QUALITIES[quality])
    if SCALE is None:
        SCALE = Image.open("util/scale.png")
        SCALE = SCALE.resize((int(SCALE.size[0] * (quality + 1)), int(QUALITIES[quality][1] * 0.6)))
    frame = Image.alpha_composite(BACKGROUND, Image.open(src).resize(BACKGROUND.size))
    scale_pos = (int(frame.size[0] * .96) - SCALE.size[0], int(((1 - (SCALE.size[1] / frame.size[1])) / 2) * frame.size[1]))
    frame.paste(SCALE, scale_pos)
    fontSize = int(frame.size[1] * .034)
    font = ImageFont.truetype("util/segoeui.ttf", fontSize)
    draw = ImageDraw.Draw(frame)
    text = when.strftime("%Y-%m-%d %H:%M")
    width, height = draw.textsize(text, font=font)
    margin = fontSize // 4
    draw.text((frame.size[0] - width - margin, frame.size[1] - height - margin), text, (0, 0, 0), font=font)
    txt_min = str(round(extrema[0], 2)) + "°C "
    width, height = draw.textsize(txt_min, font=font)
    draw.text((scale_pos[0] - width, scale_pos[1] + ((1 - ((scale_pos[1] / frame.size[1]) * 2)) * frame.size[1]) - height), txt_min, (0, 0, 0), font=font)
    txt_max = str(round(extrema[1], 2)) + "°C "
    width, height = draw.textsize(txt_max, font=font)
    draw.text((scale_pos[0] - width, scale_pos[1]), txt_max, (0, 0, 0), font=font)
    frame.save(dst)

def build_animation(key: str, when: datetime, *, ffmpeg, **kwargs):
    base = layer_path(when, key).parent
    src = base / f"{key}_frames.txt"
    if not src.exists():
        return
    dst = base / f"{key}.mp4"
    if dst.exists():
        return
    args = [
        ffmpeg,
        '-y',
        '-r', '6',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(src.resolve()),
        '-c:v', 'libx264',
        '-vf', '"fps=60,format=yuv420p,scale=1920:-2"',
        str(dst.resolve()),
    ]
    try:
        subprocess.run([ffmpeg, '-version'])
    except FileNotFoundError:
        print("ffmpeg not found in path. Either provide a path to ffmpeg or run the following command manually:")
        print(" ".join(args))
        return
    print("Rendering day  using ffmpeg", end="", flush=True)
    r = subprocess.run(args)
    print("done", flush=True)


