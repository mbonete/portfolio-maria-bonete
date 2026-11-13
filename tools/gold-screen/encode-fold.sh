#!/bin/zsh
# Encodes fold/o-*.png (render-fold.sh) into public/lab/f/fold/: every frame cropped to one box (all
# frames' visible pixels, shadow included, plus a margin) so they stack exactly. Each frame becomes a
# back plate (the whole screen) and a front plate (only the panels folding toward the viewer, from
# its matte); the page sets the name between them. The open frame also ships large for the still.
set -e
D=${0:A:h}; P=$D/../../public/lab/f/fold; mkdir -p $P
frames=($D/fold/o-*.png)
box=$(for f in $frames; do magick $f -alpha extract -threshold 97% -format "%@\n" info:; done | python3 -c "
import sys, re
b = [tuple(map(int, re.split('[x+]', l.strip()))) for l in sys.stdin if l.strip()]
x0 = min(x for w, h, x, y in b); y0 = min(y for w, h, x, y in b)
x1 = max(x + w for w, h, x, y in b); y1 = max(y + h for w, h, x, y in b)
W, H = x1 - x0, y1 - y0; mx, mt, mb = W * 3 // 100, H * 3 // 100, H * 9 // 100
print(f'{W + 2 * mx}x{H + mt + mb}+{x0 - mx}+{y0 - mt}')")
echo "crop $box"
# fade the shadow catcher's far floor to nothing at the crop's sides and bottom
FX="u>=0.98 ? u : max(0,(u-0.1)*1.4) * min(1, min(i, w-1-i)/(0.05*w)) * min(1, (h-1-j)/(0.07*h))"
enc() { magick $1 -depth 8 -resize ${2}x $D/tmp.png; cwebp -quiet -q ${4:-84} -alpha_q 90 -sharp_yuv -m 6 $D/tmp.png -o $3; }
for f in $frames; do
  i=${${f:t:r}#o-}
  magick $f -crop $box +repage -channel A -fx "$FX" +channel $D/fold/b-$i.png
  magick $f \( $D/fold/m-$i.png -alpha extract \) -compose CopyOpacity -composite -crop $box +repage $D/fold/f-$i.png
  enc $D/fold/b-$i.png ${SEQW:-1400} $P/b-$i.webp 80
  enc $D/fold/f-$i.png ${SEQW:-1400} $P/f-$i.webp 80
done
last=${${frames[-1]:t:r}#o-}
for w in 2360 1770 1180; do
  enc $D/fold/b-$last.png $w $P/open-$w.webp
  enc $D/fold/f-$last.png $w $P/open-front-$w.webp
done
magick identify -format "%wx%h\n" $P/open-2360.webp $P/b-00.webp
du -sh $P
rm -f $D/tmp.png
