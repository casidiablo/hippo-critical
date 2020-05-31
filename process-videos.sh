#!/usr/bin/env bash

set -euo pipefail

# it just creates the video files
plan=$(./prepare-recordings.py)
# and now we can actually upload them to YouTube
while read line;
do
    video_path=$(echo "$line" | jq '.video')
    title=$(echo "$line" | jq '.title')
    echo python youtube-upload-master/bin/youtube-upload \
      --title $title \
      --client-secrets=/home/cristian/recordings/client_secret.json \
      --credentials-file=/home/cristian/recordings/youtube-upload-credentials.json \
      --privacy private \
      $video_path
done <<< "$plan"