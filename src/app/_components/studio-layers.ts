// Written by tools/studio/encode-layers.sh from layers.py's renders: where the hero's interactive layers
// sit in the studio's 2400 x 1162 px frame. The images are public/studio/<name>-<studio width>.webp.
export const FRAME = { w: 2400, h: 1162 } as const;

// What moves or lights up, cut to its own box.
export const LAYERS = {
  conga: { x: 1778, y: 555, w: 191, h: 412 },
  maracas: { x: 1631, y: 923, w: 155, h: 73 },
  keys: { x: 855, y: 444, w: 438, h: 145 },
} as const;

// Each object's own box (the keyboard's, not its light's), for the focus ring.
export const TARGETS = {
  conga: { x: 1778, y: 555, w: 191, h: 412 },
  maracas: { x: 1631, y: 923, w: 155, h: 73 },
  keys: { x: 981, y: 526, w: 215, h: 30 },
} as const;
