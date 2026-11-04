#!/bin/zsh
# Renders the four lights for desktop (3840 x 3600) and phone (1560 x 4560) with a 1 px pixel filter.
D=${0:A:h}; cd $D; mkdir -p lights4; B=/Applications/Blender.app/Contents/MacOS/Blender
export FIGX=0.04 SPOT=40 BLEND=0.7 GESSO=0.14 EXPO=-0.7 FILTER=1.0
typeset -A L
L[gold]="LAMPC=1.0,0.70,0.30 WALLC=1.0,0.74,0.38 KEY=480 WALL=45"
L[sunset]="LAMPC=1.0,0.34,0.08 WALLC=1.0,0.40,0.14 KEY=640 WALL=60"
L[dusk]="LAMPC=0.52,0.46,1.0 WALLC=0.40,0.50,1.0 KEY=800 WALL=78 EXPO=-0.55"
L[daylight]="LAMPC=0.80,0.90,1.0 WALLC=0.82,0.90,1.0 KEY=500 WALL=52 EXPO=-0.6"
for n in ${=LIGHTS:-gold sunset dusk daylight}; do
  env ${=L[$n]} CAMD=5.0 SHX=-0.24 BASEH=2400 $B -b --factory-startup -P scene.py -- $D/lights4/d-$n.png 3840 3600 desktop ${SAMPLES:-512} 2>&1 | grep -E "SAVED|rror"
  env ${=L[$n]} BASEH=3376 $B -b --factory-startup -P scene.py -- $D/lights4/m-$n.png 1560 4560 mobile ${SAMPLES:-512} 2>&1 | grep -E "SAVED|rror"
done
