#!/bin/zsh
# Encodes a studio render (transparent, with the shadow-catcher floor) into public/studio/<name>-<w>.webp.
# The catcher leaves a faint tone over the whole floor, which would show the image's edges as a
# rectangle on the page's ground: the floor's alpha is lifted off that tone and faded out towards the
# sides and bottom. The objects' solid pixels, and a rim of anti-aliased edge around them, keep the
# alpha Blender gave them.
# Usage: encode.sh renders/scene.png name
set -e
D=${0:A:h}; P=$D/../../public/studio; mkdir -p $P; T=$D/renders/tmp
src=$1; name=$2
FX="u>=0.98 ? u : max(0,(u-${LIFT:-0.05})*${GAIN:-1.25}) * min(1, min(i, w-1-i)/(0.08*w)) * min(1, (h-1-j)/(0.10*h))"
magick $src -depth 16 $T-c.png
magick $T-c.png -alpha extract $T-a.png
magick $T-a.png -fx "$FX" $T-r.png
magick $T-a.png -threshold 97.9% -morphology Dilate Disk:2 $T-m.png
magick $T-r.png $T-a.png $T-m.png -composite $T-a.png
magick $T-c.png $T-a.png -alpha off -compose CopyOpacity -composite $T-o.png
for w in ${=WIDTHS:-1200 1800 2400}; do
  magick $T-o.png -depth 8 -resize ${w}x $T.png
  cwebp -quiet -q ${Q:-84} -alpha_q 90 -sharp_yuv -m 6 $T.png -o $P/$name-$w.webp
done
magick identify -format "%wx%h\n" $P/$name-${${=WIDTHS:-1200 1800 2400}[-1]}.webp
ls -la $P | grep $name
rm -f $T.png $T-[cramo].png
