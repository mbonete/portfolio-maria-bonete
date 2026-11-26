#!/bin/zsh
# One of the hero's sounds, cut from a CC0 recording (ASSETS.md lists each source): trimmed to the
# stretch that is used, a 4 ms fade in and a 60 ms fade out so it starts and stops without a click,
# mixed to mono and levelled to a peak, 44.1 kHz MP3 (every browser decodes it) in public/studio/<name>.mp3.
# Usage: sounds.sh NAME SOURCE START SECONDS [PEAK_DB]
#   sounds.sh conga 512073_2771755-hq.mp3 0 0.75 -4   (the cuts used are in ASSETS.md)
set -e
D=${0:A:h}; P=$D/../../public/studio; mkdir -p $P
name=$1; src=$2; start=$3; dur=$4; peak=${5:--3}
# to mono first, as float, on its own: inside one filter chain ffmpeg mixes the channels differently
# depending on what follows, so the level measured would not be the level written
m=$(mktemp -t sound).wav
ffmpeg -hide_banner -loglevel error -y -i $src -ac 1 -c:a pcm_f32le $m
src=$m
f="atrim=start=$start:duration=$dur,asetpts=N/SR/TB,afade=t=in:d=0.004,afade=t=out:st=$(printf %.3f $(( dur - 0.06 ))):d=0.06"
# the peak from astats, which reads the float samples (volumedetect clips them at 0 dB first)
max=$(ffmpeg -hide_banner -i $src -af "$f,astats" -f null - 2>&1 | sed -n 's/.*Peak level dB: \(-*[0-9.]*\).*/\1/p' | tail -1)
ffmpeg -hide_banner -loglevel error -y -i $src -af "$f,volume=$(printf %.2f $(( peak - max )))dB" -ar 44100 \
  -c:a libmp3lame -q:a 4 $P/$name.mp3
ffprobe -hide_banner -v error -show_entries format=duration,size -of csv=p=0 $P/$name.mp3 | sed "s|^|$name.mp3 (s, bytes): |"
rm -f $m
