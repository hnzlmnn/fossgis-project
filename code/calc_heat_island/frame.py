import subprocess

from PIL import Image, ImageFont, ImageDraw
from datetime import datetime

from calc_heat_island.data import layer_path
from .util import QUALITIES


BACKGROUND = None
SCALE = None

def store_frame_txt(algo: str, key: str, frame_path):
    txt = frame_path.parent / f"{key}_{algo}_frames.txt"
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
        SCALE = SCALE.resize((SCALE.size[0], int(QUALITIES[quality][1] * .95)))
    frame = Image.alpha_composite(BACKGROUND, Image.open(src).resize(BACKGROUND.size))
    fontSize = int(frame.size[1] * .034)
    font = ImageFont.truetype("util/segoeui.ttf", fontSize)
    width, height = frame.size
    margin = fontSize // 4
    draw = ImageDraw.Draw(frame)
    # Date
    txt_date = when.strftime("%Y-%m-%d %H:%M")
    w0, h0 = draw.textsize(txt_date, font=font)
    # Min
    txt_min = str(round(extrema[0], 2)) + "°C "
    w1, h1 = draw.textsize(txt_min, font=font)
    # Max
    txt_max = str(round(extrema[1], 2)) + "°C "
    w2, _ = draw.textsize(txt_max, font=font)
    # Calculate new size
    width += int(SCALE.size[0] + 3 * margin + max(w1, w2))
    height += int(h0 + 2 * margin)
    final = Image.new("RGB", (width, height), (255, 255, 255))
    # Scale
    scale_pos = (
        int(width - margin - SCALE.size[0]),
        int(((1 - (SCALE.size[1] / final.size[1])) / 2) * final.size[1]),
    )
    final.paste(frame, (0, final.size[1] - frame.size[1]))
    final.paste(SCALE, scale_pos)
    # Positions
    date_pos = (int(width / 2 - w0 / 2), margin)
    min_pos = (int(scale_pos[0] - w1 - margin), scale_pos[1] + SCALE.size[1] - h1)
    max_pos = (int(scale_pos[0] - w2 - margin), scale_pos[1])
    # Draw text
    draw = ImageDraw.Draw(final)
    draw.text(date_pos, txt_date, (0, 0, 0), font=font)
    draw.text(min_pos, txt_min, (0, 0, 0), font=font)
    draw.text(max_pos, txt_max, (0, 0, 0), font=font)

    final.save(dst)

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


