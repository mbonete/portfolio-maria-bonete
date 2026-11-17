#!/bin/zsh
# The screen folding shut, as a sequence for the page to scrub: N renders from nearly closed (CLOSED
# degrees) to open (OPEN), spaced so its width grows evenly, under one warm lamp. Each frame also
# gets a matte of the two panels that
# fold toward the viewer, so the page can thread the name through the folds at every frame. Her
# silhouette fades out over the first half of the shutting (MATTE=0 re-renders without the mattes,
# which do not change with it). The light deepens as it opens: shut, the leaf mirrors a pale room;
# open, a dark one (WORLDC) lit by a brighter candle wall (WALL), so the panels turned away from the
# lamp fall into shadow and the panels alternate gold and dark.
D=${0:A:h}; cd $D; mkdir -p fold; B=/Applications/Blender.app/Contents/MacOS/Blender
export FIGX=0.04 SPOT=40 BLEND=0.7 GESSO=0.14 EXPO=-0.45 FILTER=1.0 CUTOUT=1 OPEN=${OPEN:-26}
export LAMPC=1.0,0.70,0.30 WALLC=1.0,0.74,0.38 KEY=480
N=${N:-28}; CLOSED=${CLOSED:-80}
for k in $(seq ${FROM:-0} ${TO:-$((N - 1))}); do
  f=$(python3 -c "import math; c=math.cos(math.radians($CLOSED)); o=math.cos(math.radians($OPEN)); print(math.degrees(math.acos(c + (o - c) * $k / ($N - 1))))")
  sil=$(python3 -c "t=min(max(($k/($N-1)-0.5)/0.5,0),1); print(round(t*t*(3-2*t),4))")
  read worldc wall <<< $(python3 -c "t=$k/($N-1); a,b=(0.62,0.70,0.95),(0.12,0.13,0.18); print(','.join(f'{x+(y-x)*t:.4f}' for x,y in zip(a,b)), round(45+50*t,2))")
  i=$(printf %02d $k)
  SIL=$sil WORLDC=$worldc WALL=$wall $B -b --factory-startup -P scene.py -- $D/fold/o-$i.png ${W:-2400} ${H:-1350} object ${SAMPLES:-64} $f 2>&1 | grep -E "SAVED|rror"
  [[ ${MATTE:-1} = 0 ]] || FRONT=1,3 DENOISE=0 $B -b --factory-startup -P scene.py -- $D/fold/m-$i.png ${W:-2400} ${H:-1350} object 16 $f 2>&1 | grep -E "SAVED|rror"
done
