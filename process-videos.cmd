#!/usr/bin/env bash
# @from Dockerfile
# @group Personal
# @description Concats all the videos in the provided folder and pushes them to Youtube
# @user root
# @needs_tty true
# @version 0.1.0
# @enable_dynamic_volume_mounts true
# @vol ~/.config/youtube:/youtube-config:ro
# @vol ~/.timewarrior:/timewarrior:ro

set -euo pipefail

# These are mounted on read-only-mode for security
# so I copied them inside the container to make them writable
cp -r /timewarrior /root/.timewarrior
cp -r /youtube-config /youtube

. argsparse.sh

argsparse_use_option =rec-dir: "Directory of the recordings to process" mandatory

# parse all the options. exits if invalid
argsparse_parse_options "$@"

directory=${program_options[rec-dir]}

# Directory where files are processed
mkdir /workspace

# Run script that merges and uploads the video
python3 upload-recordings.py "$directory"
