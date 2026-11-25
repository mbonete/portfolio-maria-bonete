#!/bin/zsh
# Renders an object's turntable views and lays them out on the page's azurite as one sheet.
# Usage: turntable.sh NAME [WIDTH=1200] [SAMPLES=128]  ->  renders/tt-NAME.png
set -e
D=${0:A:h}; B=/Applications/Blender.app/Contents/MacOS/Blender; mkdir -p $D/renders
n=$1; w=${2:-1200}; s=${3:-128}; o=$D/renders/tt-${n//,/-}
$B -b --factory-startup -P $D/turntable.py -- $n $o $w $s 2>&1 | grep -E "SAVED|rror|Traceback" || true
for v in front left right close; do magick $o-$v.png -background '#6581df' -flatten -depth 8 $o-$v-flat.png; done
magick \( $o-front-flat.png $o-left-flat.png +append \) \( $o-right-flat.png $o-close-flat.png +append \) -append $o.png
rm -f $o-*-flat.png
echo "SHEET $o.png"
