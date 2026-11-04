#!/bin/zsh
# Encodes lights4/ into the site's image set. sharp_yuv keeps the saturated edges from smearing
# when WebP halves the colour resolution.
set -e
D=${0:A:h}; P=$D/../../public/lab/e
for n in gold sunset dusk daylight; do
  for w in 3840 2880 2560 1600; do
    magick $D/lights4/d-$n.png -depth 8 -resize ${w}x $D/tmp.png
    cwebp -quiet -q 86 -sharp_yuv -m 6 $D/tmp.png -o $P/light-$n-$w.webp
  done
  for w in 1560 1170 780; do
    magick $D/lights4/m-$n.png -depth 8 -resize ${w}x $D/tmp.png
    cwebp -quiet -q 86 -sharp_yuv -m 6 $D/tmp.png -o $P/light-$n-m$w.webp
  done
done
rm -f $D/tmp.png
