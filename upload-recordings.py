#!/usr/bin/env python
import subprocess
from os import listdir
from os.path import isfile, join
from dateutil import parser
import datetime
from dateutil.tz import tzlocal
import json
from sys import stderr
import sys
import os
from pytz import timezone

# list all video files
dir=sys.argv[1]
workspace_folder="/tmp"
video_files = [f"{dir}/{f}" for f in listdir(dir) if isfile(f"{dir}/{f}") and f.endswith(".mkv")]

# group files by day and extract their length
videos_to_upload = {}
for video in video_files:
    filename = os.path.basename(video)
    start_time = filename.replace(".mkv", "")
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
    destination_video = f"{workspace_folder}/{date}.mkv"
    subprocess.call(f"rm {destination_video} 2> /dev/null", shell=True) # just in case

    if len(videos) == 1:
        # just copy file to destination
        subprocess.check_output(f"cp {videos[0]['filename']} {destination_video}", shell=True)
    else:
        sorted_videos = [v['filename'] for v in sorted(videos, key=lambda vid: vid['filename'])]
        for idx, video in enumerate(sorted_videos):
            print(f"Processing {video}", file=stderr)
            if idx == 0:
                subprocess.check_output(f"mkvmerge -o {workspace_folder}/{date}.mkv {video} +{sorted_videos[idx+1]}; exit 0", shell=True)
            elif idx != len(videos) - 1:
                subprocess.check_output(f"mkvmerge -o {workspace_folder}/{date}_temp.mkv {workspace_folder}/{date}.mkv +{sorted_videos[idx+1]}; exit 0", shell=True)
                subprocess.check_output(f"mv {workspace_folder}/{date}_temp.mkv {workspace_folder}/{date}.mkv", shell=True)

    # attach metadata for this video from timewarrior
    timew_json = subprocess.check_output(["timew", "export"])
    tags_hist = {}
    for record in json.loads(timew_json):
        # drop records that are not of this date
        record_start = record['start']
        record_start_date = parser.parse(record_start).astimezone(timezone('US/Pacific')).date()
        if str(record_start_date) == str(date) and 'tags' in record:
            for tag in record['tags']:
                tag_count = tags_hist.get(tag, 0) + 1
                tags_hist[tag] = tag_count
    title = [tag[0] for tag in sorted(tags_hist.items(), key=lambda item: item[1], reverse=True)][:2]
    title = sorted(title, key=len)
    title = map(lambda tag: f"[{tag}]" if len(tag.split(" ")) == 1 else tag, title)
    title = ' '.join(title)

    # since processing was successful, upload full video
    subprocess.check_output(f"""python3 /app/youtube-upload/bin/youtube-upload \
      --title "[{date}] {title}" \
      --client-secrets=/tmp/.youtube/client_secret.json \
      --credentials-file=/tmp/.youtube/youtube-upload-credentials.json \
      --privacy private \
      "{destination_video}" """, shell=True)
    
    # if uploading finished successfully, delete originals
    for vid in videos:
        subprocess.call(f"rm {vid['filename']}", shell=True)
