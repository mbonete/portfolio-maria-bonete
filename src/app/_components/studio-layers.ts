// Written by tools/studio/encode-layers.sh from layers.py's renders: where the hero's interactive layers
// sit in the studio's 2400 x 1164 px frame. The images are public/studio/<name>-<studio width>.webp.
export const FRAME = { w: 2400, h: 1164 } as const;

// Cut-outs that move, each over the room where it stands.
export const CUTOUTS = {
  capybara: { x: 1037, y: 679, w: 230, h: 317 },
  conga: { x: 1778, y: 557, w: 190, h: 412 },
  maracas: { x: 1630, y: 925, w: 155, h: 72 },
  monstera: { x: 275, y: 167, w: 653, h: 748 },
} as const;

// Light added over the room: the keyboard's LEDs flaring, the camera's flash.
export const LIGHTS = {
  keys: { x: 871, y: 448, w: 425, h: 142 },
  flash: { x: 993, y: 504, w: 786, h: 451 },
} as const;

// Variants shown in place, one after another: the computer's LED colours, the painting's stages.
export const SWAPS = {
  tower: { ...{ x: 1559, y: 211, w: 331, h: 397 }, count: 3 },
  easel: { ...{ x: 1873, y: 241, w: 459, h: 379 }, count: 3 },
} as const;

// The monstera's breeze: frames monstera-f01 to -f19 at this rate, at studio width 1200.
export const BREEZE = { fps: 15, frames: 19 } as const;

// Where the flash fires, for its burst.
export const FLASH_HEAD = { x: 1380, y: 629 } as const;

// hit.png: a quarter-size map, each thing's grey value HIT_GREY times its number here.
export const HIT = { conga: 1, maracas: 2, keys: 3, capybara: 4, camera: 5, tower: 6, easel: 7, monstera: 8, monitors: 9 } as const;
export const HIT_GREY = 25;

// Each thing's own box (its silhouette's), for the focus ring.
export const TARGETS = {
  conga: { x: 1784, y: 563, w: 178, h: 400 },
  maracas: { x: 1636, y: 931, w: 143, h: 60 },
  keys: { x: 979, y: 527, w: 215, h: 30 },
  capybara: { x: 1043, y: 685, w: 218, h: 305 },
  camera: { x: 1337, y: 621, w: 89, h: 69 },
  tower: { x: 1656, y: 294, w: 138, h: 256 },
  easel: { x: 1873, y: 59, w: 455, h: 860 },
  monstera: { x: 290, y: 185, w: 609, h: 722 },
  monitors: { x: 805, y: 113, w: 833, h: 329 },
} as const;
