#!/bin/zsh
# Encodes layers.py's renders for the hero:
#   base.png              -> public/studio/studio-{1200,1800,2400}.webp (through encode.sh, floor and all)
#   conga.png, maracas.png -> public/studio/<name>-{1200,1800,2400}.webp, cut to the object, alpha kept
#   keys-lit-K - keys-base -> public/studio/keys-{1200,1800,2400}.webp, the LEDs' extra light (as colour
#                            and alpha), for the page to add on top (mix-blend-mode: plus-lighter); K picks
#                            the brightness
#   the three silhouettes -> public/studio/hit.png at a quarter size: red the conga, green the maracas,
#                            blue the keyboard
# and writes where each sits, in the 2400 px frame, to src/app/_components/studio-layers.ts.
# The -{1200,1800,2400} suffix names the studio width a file goes with, not its own width.
# Usage: [KEYS_K=10] encode-layers.sh [renders/layers]
set -e
D=${0:A:h}; L=${1:-$D/renders/layers}; P=$D/../../public/studio; TS=$D/../../src/app/_components/studio-layers.ts
T=$D/renders/tmp-layers; mkdir -p $P $T
read W H <<< "$(magick identify -format "%w %h" $L/base.png)"

Q=${Q:-90} $D/encode.sh $L/base.png studio >/dev/null

# cut: image, name, pad -> crops to the object (its pixels over half opaque, padded), drops the faint
# alpha that held-out glass and edges leave elsewhere (under 3%), writes the three sizes, prints
# "x y w h" (in the full frame)
cut() {
  local g=$(magick $1 -alpha extract -threshold 50% -format "%@" info:)
  local w=${${g%%x*}}; local rest=${g#*x}; local h=${rest%%+*}; rest=${rest#*+}; local x=${rest%%+*}; local y=${rest#*+}
  x=$(( x > $3 ? x - $3 : 0 )); y=$(( y > $3 ? y - $3 : 0 ))
  w=$(( x + w + 2 * $3 > W ? W - x : w + 2 * $3 )); h=$(( y + h + 2 * $3 > H ? H - y : h + 2 * $3 ))
  magick $1 -crop ${w}x${h}+${x}+${y} +repage -channel A -level 3%,100% +channel $T/$2.png
  for s in 1200 1800 2400; do
    magick $T/$2.png -resize $(( s * 100 / W ))% $T/$2-$s.png
    cwebp -quiet -q ${Q:-90} -alpha_q 100 -exact -sharp_yuv -m 6 $T/$2-$s.png -o $P/$2-$s.webp
  done
  echo "$x $y $w $h"
}

# the keyboard's extra light, on black: inside the corner the two were rendered in, feathered 24 px in from
# its edges (the denoiser leaves stray pixels there), then cropped to where it is more than a trace
read bx0 by0 bx1 by1 <<< "$(python3 -c "import json; print(*json.load(open('$L/layout.json'))['keys_border_px'])")"
magick $L/keys-lit-${KEYS_K:-10}.png $L/keys-base.png -alpha off -crop $((bx1 - bx0))x$((by1 - by0))+$bx0+$by0 +repage \
  -fx "max(u-v-0.003,0) * min(1, min(min(i, w-1-i), min(j, h-1-j)) / 24)" $T/keys-full.png
g=$(magick $T/keys-full.png -fuzz 1% -format "%@" info:)
magick $T/keys-full.png -crop $g +repage $T/keys-add.png
# as light with no ground of its own: alpha is the brightest channel, colour the light's hue at full
# strength, so colour x alpha is the added light and nothing opaque covers the floor's soft shadow
magick $T/keys-add.png -separate -evaluate-sequence max $T/keys-a.png
magick $T/keys-add.png -channel RGB -fx "u / max(max(max(u.r, u.g), u.b), 0.0001)" +channel $T/keys-a.png -alpha off \
  -compose CopyOpacity -composite $T/keys.png
kx=${g#*+}; ky=${kx#*+}; kx=${kx%%+*}; kw=${g%%x*}; kh=${${g#*x}%%+*}
kx=$((kx + bx0)); ky=$((ky + by0))
for s in 1200 1800 2400; do
  magick $T/keys.png -resize $(( s * 100 / W ))% $T/keys-$s.png
  cwebp -quiet -q ${Q:-90} -alpha_q 100 -sharp_yuv -m 6 $T/keys-$s.png -o $P/keys-$s.webp
done

conga=$(cut $L/conga.png conga 6)
maracas=$(cut $L/maracas.png maracas 6)
kbox=$(magick $L/keys-mask.png -alpha extract -threshold 50% -format "%@" info:)
kbx=${kbox#*+}; kby=${kbx#*+}; kbx=${kbx%%+*}; kbw=${kbox%%x*}; kbh=${${kbox#*x}%%+*}

# the hit map: each silhouette's alpha, a quarter size, as one channel
for n in conga maracas keys-mask; do
  magick $L/$n.png -alpha extract -resize 25% -threshold 50% $T/hit-$n.png
done
magick $T/hit-conga.png $T/hit-maracas.png $T/hit-keys-mask.png -combine -depth 8 -define png:compression-level=9 $P/hit.png

box() { local a=(${=1}); echo "{ x: $a[1], y: $a[2], w: $a[3], h: $a[4] }"; }
cat > $TS <<EOF
// Written by tools/studio/encode-layers.sh from layers.py's renders: where the hero's interactive layers
// sit in the studio's ${W} x ${H} px frame. The images are public/studio/<name>-<studio width>.webp.
export const FRAME = { w: ${W}, h: ${H} } as const;

// What moves or lights up, cut to its own box.
export const LAYERS = {
  conga: $(box "$conga"),
  maracas: $(box "$maracas"),
  keys: $(box "$kx $ky $kw $kh"),
} as const;

// Each object's own box (the keyboard's, not its light's), for the focus ring.
export const TARGETS = {
  conga: $(box "$conga"),
  maracas: $(box "$maracas"),
  keys: $(box "$kbx $kby $kbw $kbh"),
} as const;
EOF
cat $TS
ls -la $P | grep -E "conga|maracas|keys|hit|studio"
rm -rf $T
