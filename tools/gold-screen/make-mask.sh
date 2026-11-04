#!/bin/zsh
# Builds figure2.png, the shadow caster's alpha matte, from the owner-supplied silhouette image
# (it already carries alpha). The bottom 140 px fade out so the shadow has no hard cut at the waist.
# usage: ./make-mask.sh <silhouette.png>
set -e
D=${0:A:h}
magick "$1" -alpha extract $D/mask.png
magick $D/mask.png \( -size 1085x1309 xc:white -size 1085x140 gradient:white-black -append \) -compose multiply -composite $D/mask-f.png
magick -size 1085x1449 xc:black $D/mask-f.png -alpha off -compose copy_opacity -composite PNG32:$D/figure2.png
rm $D/mask.png $D/mask-f.png
