"use client";

import { useSyncExternalStore } from "react";

// The lamp's colour as one continuous position: 0 gold, 1 dusk, 2 sunset, 3 daylight, 4 = gold again.
// The screen and the track share it; per-frame updates go straight to the DOM, not through React.
export const LIGHTS = [
  { id: "gold", label: "Gold", accent: [0xd8, 0xb0, 0x61] },
  { id: "dusk", label: "Dusk", accent: [0xb7, 0xa5, 0xf0] },
  { id: "sunset", label: "Sunset", accent: [0xec, 0x8a, 0x4c] },
  { id: "daylight", label: "Daylight", accent: [0xec, 0xe0, 0xc4] },
] as const;

export const MS_PER_LIGHT = 2500;

type FrameListener = (p: number) => void;

let position = 0;
let userPlaying: boolean | null = null; // null: follow the motion preference
const frameListeners = new Set<FrameListener>();
const stateListeners = new Set<() => void>();

export const light = {
  get position() {
    return position;
  },
  setPosition(p: number) {
    position = ((p % LIGHTS.length) + LIGHTS.length) % LIGHTS.length;
    frameListeners.forEach((f) => f(position));
  },
  onFrame(f: FrameListener) {
    frameListeners.add(f);
    f(position);
    return () => {
      frameListeners.delete(f);
    };
  },
  setPlaying(v: boolean) {
    userPlaying = v;
    stateListeners.forEach((f) => f());
  },
};

const subscribeState = (f: () => void) => {
  stateListeners.add(f);
  return () => {
    stateListeners.delete(f);
  };
};

const reducedQuery = "(prefers-reduced-motion: reduce)";
const subscribeReduced = (cb: () => void) => {
  const mq = window.matchMedia(reducedQuery);
  mq.addEventListener("change", cb);
  return () => mq.removeEventListener("change", cb);
};

export function useReducedMotion() {
  return useSyncExternalStore(
    subscribeReduced,
    () => window.matchMedia(reducedQuery).matches,
    () => false,
  );
}

/** Whether the light should flow: the visitor's choice, else on unless they prefer reduced motion. */
export function usePlaying() {
  const reduced = useReducedMotion();
  const chosen = useSyncExternalStore(
    subscribeState,
    () => userPlaying,
    () => null,
  );
  return chosen ?? !reduced;
}

/** Name for a position: the light it is on, or the two it is between. */
export function describe(p: number) {
  const i = Math.floor(p) % LIGHTS.length;
  const f = p - Math.floor(p);
  if (f < 0.12) return LIGHTS[i].label;
  if (f > 0.88) return LIGHTS[(i + 1) % LIGHTS.length].label;
  return `Between ${LIGHTS[i].label} and ${LIGHTS[(i + 1) % LIGHTS.length].label}`;
}

export function accentAt(p: number) {
  const i = Math.floor(p) % LIGHTS.length;
  const f = p - Math.floor(p);
  const a = LIGHTS[i].accent;
  const b = LIGHTS[(i + 1) % LIGHTS.length].accent;
  return `rgb(${a.map((v, k) => Math.round(v + (b[k] - v) * f)).join(" ")})`;
}
