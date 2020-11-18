import subprocess
import csv
from pathlib import Path
from datetime import datetime, timedelta
import json


fast = False

        
def render(src, dst, start, end, date, title, comment, location):
    args = (
            ["ffmpeg"] +
            ["-ss", str(start.total_seconds())] +
            ["-to", str(end.total_seconds())] +
            ["-i", src] +
            ["-metadata", "title=" + title] +
            ["-metadata", "comment=" + comment] +
            ["-metadata", "creation_time=" +  date.strftime("%Y-%m-%d %H:%M:%S")])

    if location:
        location_str = "{:+02.4f}{:+03.4f}/".format(*location)
        args += (
            ["-metadata", "location=" + location_str] +
            ["-metadata", "location_eng=" + location_str])


    if fast:
        args += ["-vf", "scale=iw/8:ih/8"] 
    args += [dst]
    subprocess.check_call(args)


def parse_time(s):
    h, m, s = s.split(":")
    return timedelta(
            hours=int(h),
            minutes=int(m),
            seconds=float(s)
            )

def split_video(src, dst, meta, time_offset=-(timedelta(seconds=1)/30)):
    src = Path(src)
    dst = Path(dst)
    scenes = list()
    with open(meta, "r") as f:
        for i, row in enumerate(csv.DictReader(f)):
            scene = row
            scene["number"] = i + 1
            scenes.append(row)
    
    #scenes = scenes[43:45]

    for scene in scenes:
        if scene["Description"] == "blank":
            continue
        if scene["Latitude"]:
            location= (float(scene["Latitude"]), float(scene["Longitude"]))
        else:
            location = None
        if scene["Date"]:
            date = datetime.strptime(scene["Date"], "%Y-%m-%d")
            date = date.replace(hour=12)
        else:
            date = None
        start = parse_time(scene["Video Start Time"])
        end = parse_time(scene["Video End Time"])
        start += time_offset
        end += time_offset

        # adjust endtime by one frame
        end -= timedelta(seconds=1) / 30

        name = " - ".join([
            date.strftime("%Y-%m-%d"),
            src.stem,
            "{:03d}".format(scene["number"]),
            scene["Description"]
            ])
        path = dst / (name + ".mp4")
        comment = [
                ("original", src.stem),
                ("scene", scene["number"]),
                ("scene_start", scene["Video Start Time"]),
                ("location", scene["Location"]),
                ("date", scene["Date"])
            ]
        render(src, path,
                start=start,
                end=end,
                date=date,
                title=scene["Description"],
                comment = json.dumps(comment),
                location=location)


original_videos = Path("/media/aaron/Storage/trove/original videos/done")

#source = "Family 1992_002"
source = "1985 our wedding"

split_video(
        src = original_videos / (source + ".mp4"),
        dst = "/media/aaron/Storage/trove/scenes/",
        meta = "/media/aaron/Storage/trove/metadata/Family Video - " + source + ".csv")
