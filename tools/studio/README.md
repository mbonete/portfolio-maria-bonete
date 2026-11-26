# The studio (the home page hero)

A studio rendered in Blender 5.2 (Cycles) and set on the hero's azurite ground as a cut-out: every object
is built in Python, at real size, from code in this folder. The page shows `public/studio/studio-*.webp`
(the room without the conga and the maracas) with the interactive layers on top: the conga, the maracas
and the keyboard LEDs' extra light, each answering a click with a CC0 sound.

## Rebuild

1. Textures: `python3 fetch.py ...` for each Poly Haven / ambientCG id in `ASSETS.md` (all CC0; they land in
   the gitignored `assets/`). The reflection-only environment is Poly Haven `studio_small_08`
   (`python3 fetch.py polyhaven-hdri studio_small_08`).
2. The folding screen reuses the hero's old painted panels: run `../gold-screen/build.sh` first (it writes
   the gitignored `../gold-screen/p3/`).
3. The middle monitor's picture: `python3 ide.py` (headless Chrome) -> `renders/ide.png`.
4. The painting on the easel: `blender -b --factory-startup --python-exit-code 1 -P painting.py`.
5. The scene in one piece, to look at: `blender -b --factory-startup -P scene.py -- $PWD/renders/studio.png
   2400 256` (about 4.5 minutes on an M3).
6. What the page shows: `blender -b --factory-startup -P layers.py -- $PWD/renders/layers 2400 256` (about 8
   minutes) renders the room and the interactive layers from the same camera, then
   `KEYS_K=20 ./encode-layers.sh` writes their web sizes, the hit map (`hit.png`) and
   `src/app/_components/studio-layers.ts` (where each layer sits).
7. The sounds: `./sounds.sh NAME SOURCE START SECONDS [PEAK_DB]` for each (sources in `ASSETS.md`) writes
   `public/studio/NAME.mp3`.

## Files

- `common.py`: where everything stands, the camera, the lights, the shadow-catcher floor.
- `standins.py`: grey stand-ins of every object; `blockout.py` renders only those.
- `objects/<name>.py`: the finished objects; `scene.py` uses one wherever it exists.
- `turntable.sh NAME`: one object alone from four sides, for close checks.
- `layers.py`, `encode-layers.sh`: the hero's stack of renders (the room, the conga, the maracas, the
  keyboard's light) and its encoding; `src/app/_components/StudioScene.tsx` plays them.
- `sounds.sh`: trims and levels a recording into one of the hero's sounds.
