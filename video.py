import subprocess
import csv
from pathlib import Path
from datetime import datetime

        


def render_mkv(*args):
    return render_mkv(*args)


def render_mkv(src, dst, start, end):
    # these settings seem to work on google photos without causing audio issues
    subprocess.check_call(["ffmpeg"] +
            ["-ss", start] +
            ["-to", end] +
            ["-i", src] +
            ["-vf", "scale=iw*2:ih*2"] +
            ["-c:a", "aac", "-profile:a", "aac_low", "-b:a", "384k"] +
            ["-ar", "44100"] +
            ["-pix_fmt", "yuv420p", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "18", "-g", "15", "-bf", "2"] +
            ["-movflags", "faststart"] +
            [dst])


def render(src, dst, start, end, date, location):
    args = (
            ["ffmpeg"] +
            ["-ss", start] +
            ["-to", end] +
            ["-i", src] +
            ["-vf", "scale=iw*2:ih*2"] +
            ["-c:a", "aac", "-profile:a", "aac_low", "-b:a", "384k"] +
            ["-ar", "44100"] +
            ["-pix_fmt", "yuv420p", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "18", "-g", "15", "-bf", "2"] +
            ["-movflags", "faststart"] +
            ["-metadata", "creation_time=" +  date.strftime("%Y-%m-%d %H:%M:%S")])

    if location:
        location_str = "{:+02.4f}{:+03.4f}/".format(*location)
        args += (
            ["-metadata", "location=" + location_str] +
            ["-metadata", "location_eng=" + location_str])
    args += [dst]
    subprocess.check_call(args)


def render(src, dst, start, end, date, location):
    args = (
            ["ffmpeg"] +
            ["-ss", start] +
            ["-to", end] +
            ["-i", src] +
            ["-metadata", "creation_time=" +  date.strftime("%Y-%m-%d %H:%M:%S")])

    if location:
        location_str = "{:+02.4f}{:+03.4f}/".format(*location)
        args += (
            ["-metadata", "location=" + location_str] +
            ["-metadata", "location_eng=" + location_str])
    args += [dst]
    subprocess.check_call(args)


def split_video(src, dst, meta):
    src = Path(src)
    dst = Path(dst)
    scenes = list()
    with open(meta, "r") as f:
        for i, row in enumerate(csv.DictReader(f)):
            scene = row
            scene["number"] = str(i)
            scenes.append(row)
    
    # scenes = scenes[3:4]


    for scene in scenes:
        name = " - ".join([src.name, "{:03d}".format(int(scene["number"])), scene["Description"]])
        path = dst / (name + ".mp4")
        if scene["Description"] == "blank":
            continue
        if scene["Latitude"]:
            location= (float(scene["Latitude"]), float(scene["Longitude"]))
        else:
            location = None
        if scene["Date"]:
            date = datetime.strptime(scene["Date"], "%Y-%m-%d")
        else:
            date = None
        render(src, path, scene["Video Start Time"], scene["Video End Time"],
                date=date,
                location=location)



split_video(
        src = "/home/aaron/Videos/trove/Family 1992_002.mp4",
        dst = "/home/aaron/Videos/trove/dst",
        meta = "/home/aaron/Videos/trove/Family Video - Family 1992_002.csv")
