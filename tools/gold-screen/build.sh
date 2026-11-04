#!/bin/zsh
# The Gold Screen hero, end to end:
#   1. ./make-mask.sh <silhouette.png>   -> figure2.png
#   2. ./build.sh                        -> paints the panels into p3/ and renders lights4/
#   3. ./encode.sh                       -> public/lab/e/light-*.webp
# Needs Blender 5 (its bundled Python runs the painter), ImageMagick and cwebp.
set -e
D=${0:A:h}; cd $D
[ -f figure2.png ] || { echo "run ./make-mask.sh <silhouette.png> first"; exit 1; }
/Applications/Blender.app/Contents/Resources/*/python/bin/python3.13 -I paint.py p3
./render.sh
