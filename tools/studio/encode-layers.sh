#!/bin/zsh
# Encodes layers.py's renders for the hero, into public/studio/ (the -{1200,1800,2400} suffix names the
# studio width a file goes with, not its own width):
#   base.png                -> studio-*.webp, through encode.sh (floor and all)
#   capybara, conga, maracas -> <name>-*.webp, cut to the object, alpha kept
#   monstera-00..NN         -> monstera-*.webp (at rest) and monstera-fNN.webp (the breeze, studio width
#                              1200 only), all cut to one box
#   keys-lit-K - keys-base, flash-lit - flash-base
#                           -> keys-*.webp, flash-*.webp: the added light as colour and alpha, for the
#                              page to add on top (mix-blend-mode: plus-lighter)
#   tower-pN, easel-sN      -> tower-pN-*.webp, easel-sN-*.webp: each variant only where it differs from
#                              its region's base, to show in place
#   the silhouettes          -> hit.png, a quarter size, one grey per thing (HIT_GREY times its HIT number)
# and writes where each sits, in the full frame, to src/app/_components/studio-layers.ts.
# Usage: [KEYS_K=20] encode-layers.sh [renders/layers]
set -e
D=${0:A:h}; L=${1:-$D/renders/layers}; P=$D/../../public/studio; TS=$D/../../src/app/_components/studio-layers.ts
T=$D/renders/tmp-layers; mkdir -p $P $T
read W H <<< "$(magick identify -format "%w %h" $L/base.png)"
SIZES=(1200 1800 2400)
js() { python3 -c "import json,sys; d=json.load(open('$L/layout.json')); print(*eval(sys.argv[1]))" "$1"; }

Q=${Q:-90} $D/encode.sh $L/base.png studio >/dev/null

# bbox IMAGE THRESHOLD -> "x y w h" of its alpha over the threshold
bbox() {
  local g=$(magick $1 -alpha extract -threshold $2 -format "%@" info:)
  local w=${g%%x*} r=${g#*x}; local h=${r%%+*}; r=${r#*+}
  echo "${r%%+*} ${r#*+} $w $h"
}
# grow "x y w h" by a pad, inside the frame
grow() {
  local a=(${=1}) p=$2
  local x=$(( a[1] > p ? a[1] - p : 0 )) y=$(( a[2] > p ? a[2] - p : 0 ))
  local x1=$(( a[1] + a[3] + p < W ? a[1] + a[3] + p : W )) y1=$(( a[2] + a[4] + p < H ? a[2] + a[4] + p : H ))
  echo "$x $y $(( x1 - x )) $(( y1 - y ))"
}
union() {
  local x0=$W y0=$H x1=0 y1=0 b
  for b in "$@"; do local a=(${=b})
    (( a[1] < x0 )) && x0=$a[1]; (( a[2] < y0 )) && y0=$a[2]
    (( a[1] + a[3] > x1 )) && x1=$(( a[1] + a[3] )); (( a[2] + a[4] > y1 )) && y1=$(( a[2] + a[4] ))
  done
  echo "$x0 $y0 $(( x1 - x0 )) $(( y1 - y0 ))"
}
# webp NAME PNG [sizes]: the widths of a crop made at the full frame
webp() {
  local s
  for s in ${=3:-$SIZES}; do
    magick $2 -resize $(( s * 100 / W ))% $T/w.png
    cwebp -quiet -q ${Q:-90} -alpha_q 100 -sharp_yuv -m 6 $T/w.png -o $P/$1-$s.webp
  done
}
crop() { local a=(${=2}); magick $1 -crop ${a[3]}x${a[4]}+${a[1]}+${a[2]} +repage ${@:3}; }

# ---------- cut-outs: drop the faint alpha held-out glass and edges leave (under 3%) ----------
typeset -A BOX
for n in capybara conga maracas; do
  BOX[$n]=$(grow "$(bbox $L/$n.png 50%)" 6)
  crop $L/$n.png "$BOX[$n]" -channel A -level 3%,100% +channel $T/$n.png
  webp $n $T/$n.png
done
frames=($L/monstera-[0-9][0-9].png)
boxes=(); for f in $frames; do boxes+=("$(bbox $f 50%)"); done
BOX[monstera]=$(grow "$(union $boxes)" 8)
for f in $frames; do
  k=${${f:t:r}#monstera-}
  crop $f "$BOX[monstera]" -channel A -level 3%,100% +channel $T/m-$k.png
  if [[ $k == 00 ]]; then
    webp monstera $T/m-$k.png
  else
    webp monstera-f$k $T/m-$k.png 1200 && mv $P/monstera-f$k-1200.webp $P/monstera-f$k.webp
  fi
done

# ---------- light, added on top: inside the region it was rendered in, feathered 24 px in from its edges
# (the denoiser leaves stray pixels there); alpha the brightest channel, colour the light's hue at full
# strength, so colour x alpha is the added light ----------
light() {   # name lit base region
  local b=($(js "d['borders']['$4']"))
  magick $2 $3 -alpha off -crop $((b[3] - b[1]))x$((b[4] - b[2]))+$b[1]+$b[2] +repage \
    -fx "max(u-v-0.003,0) * min(1, min(min(i, w-1-i), min(j, h-1-j)) / 24)" $T/l.png
  local g=$(magick $T/l.png -fuzz 1% -format "%@" info:)
  magick $T/l.png -crop $g +repage $T/l-add.png
  magick $T/l-add.png -separate -evaluate-sequence max $T/l-a.png
  magick $T/l-add.png -channel RGB -fx "u / max(max(max(u.r, u.g), u.b), 0.0001)" +channel $T/l-a.png -alpha off \
    -compose CopyOpacity -composite $T/l-$1.png
  local x=${g#*+}; local y=${x#*+}; x=${x%%+*}; local w=${g%%x*}; local h=${${g#*x}%%+*}
  BOX[$1]="$(( x + b[1] )) $(( y + b[2] )) $w $h"
  webp $1 $T/l-$1.png
}
light keys $L/keys-lit-${KEYS_K:-20}.png $L/keys-base.png keys
light flash $L/flash-lit.png $L/flash-base.png flash

# ---------- variants shown in place: each only where it differs from its region's base by more than
# noise, the edge of that softened, all of a region's variants cut to one box ----------
swap() {   # region variant...
  local r=$1; shift
  local b=($(js "d['borders']['$r']")) v bs=()
  local rg=$((b[3] - b[1]))x$((b[4] - b[2]))+$b[1]+$b[2]
  for v in "$@"; do
    magick $L/$r-base.png $L/$r-$v.png -alpha off -crop $rg +repage -compose difference -composite \
      -separate -evaluate-sequence max -fx "u * min(1, min(min(i, w-1-i), min(j, h-1-j)) / 16)" \
      -level 0.8%,3% -morphology Dilate Disk:2 -blur 0x1.5 $T/d-$v.png
    magick $L/$r-$v.png -crop $rg +repage \( +clone -alpha extract $T/d-$v.png -compose multiply -composite \) \
      -alpha off -compose CopyOpacity -composite $T/s-$v.png
    bs+=("$(bbox $T/s-$v.png 1%)")
  done
  local u=($(grow "$(union $bs)" 4))
  # grown inside the region's own image, not the frame: a box wider than the image would stretch it
  (( u[1] + u[3] > b[3] - b[1] )) && u[3]=$(( b[3] - b[1] - u[1] ))
  (( u[2] + u[4] > b[4] - b[2] )) && u[4]=$(( b[4] - b[2] - u[2] ))
  BOX[$r]="$(( u[1] + b[1] )) $(( u[2] + b[2] )) $u[3] $u[4]"
  for v in "$@"; do
    crop $T/s-$v.png "$u[*]" $T/s-$v-c.png
    webp $r-$v $T/s-$v-c.png
  done
}
swap tower p1 p2 p3
swap easel s1 s2 s3

# ---------- the hit map: one grey per thing, the nearer drawn last ----------
typeset -A HIT; HIT=(conga 1 maracas 2 keys 3 capybara 4 camera 5 tower 6 easel 7 monstera 8 monitors 9); GREY=25
typeset -A SIL; SIL=(monitors $L/mask-monitors.png easel $L/mask-easel.png tower $L/mask-tower.png monstera $L/monstera-00.png keys $L/mask-keys.png
  camera $L/mask-camera.png conga $L/conga.png capybara $L/capybara.png maracas $L/maracas.png)
QW=$(( W / 4 )); QH=$(( H / 4 ))
magick -size ${QW}x${QH} xc:black $T/hit.png
typeset -A TGT
for n in monitors easel tower monstera keys camera conga capybara maracas; do
  magick $SIL[$n] -alpha extract -resize ${QW}x${QH}! -threshold 50% $T/m.png
  magick $T/hit.png \( $T/m.png -fill "gray($(( HIT[$n] * GREY )))" -opaque white -transparent black \) -composite $T/hit.png
  TGT[$n]=$(bbox $SIL[$n] 50%)
done
magick $T/hit.png -colorspace gray -depth 8 -define png:compression-level=9 $P/hit.png

read hx hy <<< "$(js "d['flash_head']")"
box() { local a=(${=1}); echo "{ x: $a[1], y: $a[2], w: $a[3], h: $a[4] }"; }
cat > $TS <<EOF
// Written by tools/studio/encode-layers.sh from layers.py's renders: where the hero's interactive layers
// sit in the studio's ${W} x ${H} px frame. The images are public/studio/<name>-<studio width>.webp.
export const FRAME = { w: ${W}, h: ${H} } as const;

// Cut-outs that move, each over the room where it stands.
export const CUTOUTS = {
  capybara: $(box "$BOX[capybara]"),
  conga: $(box "$BOX[conga]"),
  maracas: $(box "$BOX[maracas]"),
  monstera: $(box "$BOX[monstera]"),
} as const;

// Light added over the room: the keyboard's LEDs flaring, the camera's flash.
export const LIGHTS = {
  keys: $(box "$BOX[keys]"),
  flash: $(box "$BOX[flash]"),
} as const;

// Variants shown in place, one after another: the computer's LED colours, the painting's stages.
export const SWAPS = {
  tower: { ...$(box "$BOX[tower]"), count: 3 },
  easel: { ...$(box "$BOX[easel]"), count: 3 },
} as const;

// The monstera's breeze: frames monstera-f01 to -f$(printf %02d $(( ${#frames} - 1 ))) at this rate, at studio width 1200.
export const BREEZE = { fps: $(js "[d['fps']]"), frames: $(( ${#frames} - 1 )) } as const;

// Where the flash fires, for its burst.
export const FLASH_HEAD = { x: $hx, y: $hy } as const;

// hit.png: a quarter-size map, each thing's grey value HIT_GREY times its number here.
export const HIT = { conga: 1, maracas: 2, keys: 3, capybara: 4, camera: 5, tower: 6, easel: 7, monstera: 8, monitors: 9 } as const;
export const HIT_GREY = $GREY;

// Each thing's own box (its silhouette's), for the focus ring.
export const TARGETS = {
$(for n in conga maracas keys capybara camera tower easel monstera monitors; do echo "  $n: $(box "$TGT[$n]"),"; done)
} as const;
EOF
cat $TS
du -ch $P/*.webp | tail -1
rm -rf $T
