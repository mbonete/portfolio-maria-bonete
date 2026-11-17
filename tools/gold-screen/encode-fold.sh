#!/bin/zsh
# Encodes fold/o-*.png (render-fold.sh) into public/fold/: every frame cropped to one box (all
# frames' visible pixels, shadow included, plus a margin) so they stack exactly. Each frame becomes a
# back plate (the whole screen) and a front plate (only the panels folding toward the viewer, from
# its matte); the page sets the name between them. The open frame also ships large for the still.
set -e
D=${0:A:h}; P=$D/../../public/fold; mkdir -p $P
frames=($D/fold/o-*.png)
box=$(for f in $frames; do magick $f -alpha extract -threshold 97% -format "%@\n" info:; done | python3 -c "
import sys, re
b = [tuple(map(int, re.split('[x+]', l.strip()))) for l in sys.stdin if l.strip()]
x0 = min(x for w, h, x, y in b); y0 = min(y for w, h, x, y in b)
x1 = max(x + w for w, h, x, y in b); y1 = max(y + h for w, h, x, y in b)
W, H = x1 - x0, y1 - y0; mx, mt, mb = W * 3 // 100, H * 3 // 100, H * 9 // 100
print(f'{W + 2 * mx}x{H + mt + mb}+{x0 - mx}+{y0 - mt}')")
echo "crop $box"
# A frame rendered at double size too (render-fold.sh HI=1) is encoded from that render, cropped to the
# same box doubled: scaled down, its diagonal edges come out smooth.
box2=$(python3 -c "import re; w, h, x, y = map(int, re.split('[x+]', '$box')); print(f'{2*w}x{2*h}+{2*x}+{2*y}')")
# fade the shadow catcher's far floor to nothing at the crop's sides and bottom
FX="u>=0.98 ? u : max(0,(u-0.1)*1.4) * min(1, min(i, w-1-i)/(0.05*w)) * min(1, (h-1-j)/(0.07*h))"
enc() { magick $1 -depth 8 -resize ${2}x $D/tmp.png; cwebp -quiet -q ${4:-84} -alpha_q 90 -sharp_yuv -m 6 $D/tmp.png -o $3; }
for f in $frames; do
  i=${${f:t:r}#o-}; src=$f; mat=$D/fold/m-$i.png; b=$box; rim=1.5
  [[ -f $D/fold/hi-o-$i.png && -f $D/fold/hi-m-$i.png ]] && { src=$D/fold/hi-o-$i.png; mat=$D/fold/hi-m-$i.png; b=$box2; rim=3; }
  # The fade applies to the floor only: the screen's solid pixels and a rim of anti-aliased edge around
  # them keep the alpha Blender gave them, so its diagonals do not turn into steps.
  magick $src -crop $b +repage $D/tmp-c.png
  magick $D/tmp-c.png -alpha extract $D/tmp-a.png
  magick $D/tmp-a.png -fx "$FX" $D/tmp-r.png
  magick $D/tmp-a.png -threshold 97.9% -morphology Dilate Disk:$rim $D/tmp-m.png
  magick $D/tmp-r.png $D/tmp-a.png $D/tmp-m.png -composite $D/tmp-a.png
  magick $D/tmp-c.png $D/tmp-a.png -alpha off -compose CopyOpacity -composite $D/fold/b-$i.png
  magick $src \( $mat -alpha extract \) -compose CopyOpacity -composite -crop $b +repage $D/fold/f-$i.png
  enc $D/fold/b-$i.png ${SEQW:-1400} $P/b-$i.webp 80
  enc $D/fold/f-$i.png ${SEQW:-1400} $P/f-$i.webp 80
done
last=${${frames[-1]:t:r}#o-}
# the shut and open frames also ship large, for the page to rest on
for w in 2360 1770 1180; do
  enc $D/fold/b-$last.png $w $P/open-$w.webp
  enc $D/fold/f-$last.png $w $P/open-front-$w.webp
  enc $D/fold/b-00.png $w $P/shut-$w.webp
  enc $D/fold/f-00.png $w $P/shut-front-$w.webp
done
magick identify -format "%wx%h\n" $P/open-2360.webp $P/b-00.webp
du -sh $P
rm -f $D/tmp.png $D/tmp-[cram].png
