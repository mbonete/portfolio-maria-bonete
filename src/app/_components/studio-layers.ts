// Written by tools/studio/encode-layers.sh from layers.py's renders: where the hero's interactive layers
// sit in the studio's 2400 x 1162 px frame. The images are public/studio/<name>-<studio width>.webp.
export const FRAME = { w: 2400, h: 1162 } as const;

// Cut-outs that move, each over the room where it stands.
export const CUTOUTS = {
  capybara: { x: 1039, y: 678, w: 230, h: 316 },
  conga: { x: 1779, y: 555, w: 190, h: 412 },
  maracas: { x: 1631, y: 923, w: 155, h: 73 },
  monstera: { x: 278, y: 166, w: 652, h: 747 },
} as const;

// Light added over the room: the keyboard's LEDs flaring, the camera's flash.
export const LIGHTS = {
  keys: { x: 886, y: 445, w: 408, h: 144 },
  flash: { x: 1012, y: 503, w: 768, h: 457 },
} as const;

// Variants shown in place, one after another: the computer's LED colours, the painting's stages.
export const SWAPS = {
  tower: { ...{ x: 1560, y: 212, w: 331, h: 385 }, count: 3 },
  easel: { ...{ x: 1870, y: 206, w: 461, h: 409 }, count: 3 },
} as const;

// The monstera's breeze: frames monstera-f01 to -f19 at this rate, at studio width 1200.
export const BREEZE = { fps: 15, frames: 19 } as const;

// Where the flash fires, for its burst.
export const FLASH_HEAD = { x: 1382, y: 628 } as const;

// hit.png: a quarter-size map, each thing's grey value 30 times its number here.
export const HIT = { conga: 1, maracas: 2, keys: 3, capybara: 4, camera: 5, tower: 6, easel: 7, monstera: 8 } as const;

// Each thing's own box (its silhouette's), for the focus ring.
export const TARGETS = {
  conga: { x: 1785, y: 561, w: 178, h: 400 },
  maracas: { x: 1637, y: 929, w: 143, h: 61 },
  keys: { x: 981, y: 526, w: 215, h: 30 },
  capybara: { x: 1045, y: 684, w: 218, h: 304 },
  camera: { x: 1338, y: 620, w: 89, h: 69 },
  tower: { x: 1657, y: 294, w: 137, h: 254 },
  easel: { x: 1874, y: 58, w: 454, h: 860 },
  monstera: { x: 293, y: 185, w: 608, h: 720 },
} as const;
