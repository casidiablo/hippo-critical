#!/usr/bin/env python
import subprocess
from os import listdir
from os.path import isfile, join
from dateutil import parser
import datetime
from dateutil.tz import tzlocal
import json
from sys import stderr

# list all video files
# TODO parameterize path
video_files = [f for f in listdir(".") if isfile(f) and f.endswith(".mkv")]

# group files by day and extract their length
videos_to_upload = {}
for video in video_files:
    start_time = video.replace(".mkv", "")
    date_time = datetime.datetime.strptime(start_time, '%Y-%m-%d_%H-%M-%S')
    start_date = date_time.date()

    # push video into the dictionary
    day_videos = videos_to_upload.get(start_date, [])
    day_videos.append({
        'filename': video,
        'start_time': date_time
    })
    videos_to_upload[start_date] = day_videos

# process each day individually
for date, videos in videos_to_upload.items():
    destination_video = f"preprocessed/{date}.mkv"
    subprocess.call(f"rm {destination_video}", shell=True) # just in case

    if len(videos) == 1:
        # just copy file to destination
        subprocess.check_output(f"cp {videos[0]['filename']} {destination_video}")
    else:
        sorted_videos = [v['filename'] for v in sorted(videos, key=lambda vid: vid['filename'])]
        for idx, video in enumerate(sorted_videos):
            print(f"Processing {video}", file=stderr)
            if idx == 0:
                print(f"mkvmerge -o preprocessed/{date}.mkv {video} +{sorted_videos[idx+1]}; exit 0", file=stderr)
                subprocess.check_output(f"mkvmerge -o preprocessed/{date}.mkv {video} +{sorted_videos[idx+1]}; exit 0", shell=True)
            elif idx != len(videos) - 1:
                print(f"mkvmerge -o preprocessed/{date}_temp.mkv preprocessed/{date}.mkv +{sorted_videos[idx+1]}; exit 0", file=stderr)
                subprocess.check_output(f"mkvmerge -o preprocessed/{date}_temp.mkv preprocessed/{date}.mkv +{sorted_videos[idx+1]}; exit 0", shell=True)
                subprocess.check_output(f"mv preprocessed/{date}_temp.mkv preprocessed/{date}.mkv", shell=True)
            print("done", file=stderr)

    # attach metadata for this video from timewarrior
    timew_json = subprocess.check_output(["timew", "export"])
    tags_hist = {}
    for record in json.loads(timew_json):
        # drop records that are not of this date
        record_start = record['start']
        record_start_date = parser.parse(record_start).astimezone(tzlocal()).date()
        if str(record_start_date) == str(date) and 'tags' in record:
            for tag in record['tags']:
                tag_count = tags_hist.get(tag, 0) + 1
                tags_hist[tag] = tag_count
    title = [tag[0] for tag in sorted(tags_hist.items(), key=lambda item: item[1], reverse=True)][:2]
    title = map(lambda tag: f"[{tag}]" if len(tag.split(" ")) == 1 else tag, title)
    title = ', '.join(title)
    metadata = {
        'video': f'preprocessed/{date}.mkv',
        'title': f'[{date}] {title}'
    }
    print(json.dumps(metadata))
