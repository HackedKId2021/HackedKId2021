#!/usr/bin/env bash
# Renders both cuts: output/IslandRangoli_FestiveSale_9x16.mp4 (Reels/Stories) and _16x9.mp4 (feed/YouTube).
set -euo pipefail
cd "$(dirname "$0")"
export NODE_PATH="${NODE_PATH:-$(npm root -g)}"   # uses globally installed playwright
mkdir -p build output
python3 music.py build/music.wav
for f in 9x16 16x9; do
  node render.mjs "$f" "build/silent_$f.mp4" 30 &
done
wait
for f in 9x16 16x9; do
  ffmpeg -y -loglevel error -i "build/silent_$f.mp4" -i build/music.wav -map 0:v -map 1:a \
    -c:v copy -c:a aac -b:a 192k -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -shortest -movflags +faststart \
    "output/IslandRangoli_FestiveSale_$f.mp4"
done
ls -lh output
