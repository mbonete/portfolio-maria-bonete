"use client";

import { useEffect, useRef, type MouseEvent, type PointerEvent as PointerEventR, type ReactNode } from "react";
import { FRAME, LAYERS, TARGETS } from "./studio-layers";

// Test hero (branch test/hero): the studio scene, rendered in Blender, on the blue ground under the
// name. Three things in it answer a click or tap: the conga gives a hit, the maracas a shake, the
// keyboard a burst of typing while its LEDs flare. The studio is a stack of renders from the same
// camera (tools/studio/layers.py): the room without the conga and the maracas, each of those cut out on
// top so it can move, and the LEDs' extra light, added over the room when the keyboard is typed on.
// A quarter-size map of the three silhouettes (hit.png) says what a click landed on: anything within
// REACH px of a silhouette counts, so the small maracas and the thin keyboard are easy to hit, with the
// mouse and more so with a finger. From the keyboard, each has a button of its own.

type Thing = "conga" | "maracas" | "keys";
const THINGS: Thing[] = ["conga", "maracas", "keys"];
const LABEL: Record<Thing, string> = {
  conga: "Play the conga",
  maracas: "Shake the maracas",
  keys: "Type on the keyboard",
};
const WIDTHS = [1200, 1800, 2400];
const REACH = { mouse: 18, touch: 30 }; // CSS px around each silhouette
const pct = (v: number, of: number) => `${((100 * v) / of).toFixed(4)}%`;
const at = (b: { x: number; y: number; w: number; h: number }) => ({
  left: pct(b.x, FRAME.w),
  top: pct(b.y, FRAME.h),
  width: pct(b.w, FRAME.w),
  height: pct(b.h, FRAME.h),
});

// Moves, as keyframes for the Web Animations API. The conga squashes on its foot and settles, the
// maracas rock to and fro, the LEDs flare once per burst of keys. Reduced motion keeps the sounds and
// a plain rise and fall of the LEDs.
const MOVES: Record<Thing, { frames: Keyframe[]; ms: number; still?: Keyframe[] }> = {
  conga: {
    frames: [
      { transform: "none" },
      { transform: "scale(1.012, 0.986)", offset: 0.12 },
      { transform: "scale(0.996, 1.005)", offset: 0.36 },
      { transform: "scale(1.002, 0.998)", offset: 0.62 },
      { transform: "none" },
    ],
    ms: 420,
  },
  maracas: {
    frames: [
      { transform: "none" },
      { transform: "rotate(-6deg)", offset: 0.14 },
      { transform: "rotate(5deg)", offset: 0.34 },
      { transform: "rotate(-3deg)", offset: 0.56 },
      { transform: "rotate(1.5deg)", offset: 0.76 },
      { transform: "none" },
    ],
    ms: 480,
  },
  // keys.mp3 has seven keystrokes, at 0, 0.18, 0.29, 0.43, 0.59, 0.74 and 1.01 s: the LEDs peak on each
  keys: {
    frames: [
      { opacity: 0 },
      ...[0, 0.15, 0.242, 0.358, 0.492, 0.617, 0.842].flatMap((at, k, all) => [
        { opacity: 1, offset: at + 0.02 },
        { opacity: 0.6, offset: k + 1 < all.length ? (at + all[k + 1]) / 2 + 0.02 : 0.93 },
      ]),
      { opacity: 0 },
    ],
    ms: 1200,
    still: [{ opacity: 0 }, { opacity: 1, offset: 0.15 }, { opacity: 0 }],
  },
};

// Sounds: fetched once the page is idle, decoded on the first click (a browser lets audio start only
// from one), each play a little off pitch so repeats do not sound looped.
let audio: AudioContext | null = null;
const raw = new Map<Thing, Promise<ArrayBuffer>>();
const decoded = new Map<Thing, Promise<AudioBuffer>>();

function fetchSounds() {
  for (const t of THINGS) {
    if (raw.has(t)) continue;
    const bytes = fetch(`/studio/${t}.mp3`).then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(r.status)));
    bytes.catch(() => {}); // a sound that will not load leaves the click silent, nothing more
    raw.set(t, bytes);
  }
}

function play(t: Thing) {
  if (typeof AudioContext === "undefined") return;
  audio ??= new AudioContext();
  const ctx = audio;
  void ctx.resume();
  fetchSounds();
  let buffer = decoded.get(t);
  if (!buffer) {
    buffer = raw.get(t)!.then((bytes) => ctx.decodeAudioData(bytes.slice(0)));
    decoded.set(t, buffer);
  }
  buffer
    .then((b) => {
      const src = ctx.createBufferSource();
      src.buffer = b;
      src.playbackRate.value = 0.95 + Math.random() * 0.1;
      const gain = ctx.createGain();
      gain.gain.value = 0.8;
      src.connect(gain).connect(ctx.destination);
      src.start();
    })
    .catch(() => {});
}

function Layer({ name, glow, ref }: { name: Thing; glow?: boolean; ref: (el: HTMLImageElement | null) => void }) {
  const b = LAYERS[name];
  const f = b.w / FRAME.w;
  return (
    // eslint-disable-next-line @next/next/no-img-element -- art-directed srcset, not next/image
    <img
      ref={ref}
      className={`lf-layer lf-layer-${name}${glow ? " lf-glow" : ""}`}
      src={`/studio/${name}-1200.webp`}
      srcSet={WIDTHS.map((s) => `/studio/${name}-${s}.webp ${Math.round((b.w * s) / FRAME.w)}w`).join(", ")}
      sizes={`(max-width: 760px) calc(96vw * ${f.toFixed(4)}), calc(80vw * ${f.toFixed(4)})`}
      width={b.w}
      height={b.h}
      style={{ left: pct(b.x, FRAME.w), top: pct(b.y, FRAME.h), width: pct(b.w, FRAME.w) }}
      alt=""
      aria-hidden
      draggable={false}
    />
  );
}

export default function StudioScene({ name, intro }: { name: ReactNode; intro: ReactNode }) {
  const boxRef = useRef<HTMLDivElement>(null);
  const layers = useRef<Partial<Record<Thing, HTMLImageElement | null>>>({});
  const moving = useRef<Partial<Record<Thing, Animation>>>({});
  const map = useRef<{ data: Uint8ClampedArray; w: number; h: number } | null>(null);

  useEffect(() => {
    let gone = false;
    const idle = window.requestIdleCallback?.bind(window) ?? ((f: () => void) => window.setTimeout(f, 1200));
    idle(() => {
      if (gone) return;
      fetchSounds();
      const img = new Image();
      img.src = "/studio/hit.png";
      img
        .decode()
        .then(() => {
          if (gone) return;
          const c = document.createElement("canvas");
          c.width = img.naturalWidth;
          c.height = img.naturalHeight;
          const g = c.getContext("2d", { willReadFrequently: true })!;
          g.drawImage(img, 0, 0);
          map.current = { data: g.getImageData(0, 0, c.width, c.height).data, w: c.width, h: c.height };
        })
        .catch(() => {});
    });
    return () => {
      gone = true;
    };
  }, []);

  // What is under, or within `reach` CSS px of, a point: the nearest silhouette, the
  // maracas before the conga where they overlap.
  function hit(x: number, y: number, reach: number): Thing | null {
    const m = map.current;
    const box = boxRef.current;
    if (!m || !box) return null;
    const r = box.getBoundingClientRect();
    const s = m.w / r.width;
    const mx = (x - r.left) * s;
    const my = (y - r.top) * s;
    const R = Math.max(1, Math.round(reach * s));
    let best: Thing | null = null;
    let bestD = Infinity;
    for (let dy = -R; dy <= R; dy++) {
      for (let dx = -R; dx <= R; dx++) {
        const d = dx * dx + dy * dy;
        if (d > R * R || d >= bestD) continue;
        const px = Math.round(mx + dx);
        const py = Math.round(my + dy);
        if (px < 0 || py < 0 || px >= m.w || py >= m.h) continue;
        const i = (py * m.w + px) * 4;
        const t = m.data[i + 1] > 127 ? "maracas" : m.data[i] > 127 ? "conga" : m.data[i + 2] > 127 ? "keys" : null;
        if (t) {
          best = t;
          bestD = d;
        }
      }
    }
    return best;
  }

  function act(t: Thing) {
    play(t);
    const el = layers.current[t];
    if (!el) return;
    const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const move = MOVES[t];
    const frames = still ? move.still : move.frames;
    moving.current[t]?.cancel();
    if (frames) moving.current[t] = el.animate(frames, { duration: move.ms, easing: t === "keys" ? "linear" : "ease-out" });
  }

  function onClick(e: MouseEvent) {
    const type = (e.nativeEvent as PointerEvent).pointerType;
    const touch = type ? type !== "mouse" : window.matchMedia("(pointer: coarse)").matches;
    const t = hit(e.clientX, e.clientY, touch ? REACH.touch : REACH.mouse);
    if (t) act(t);
  }

  function onPointerMove(e: PointerEventR) {
    if (e.pointerType !== "mouse" || !boxRef.current) return;
    boxRef.current.style.cursor = hit(e.clientX, e.clientY, REACH.mouse) ? "pointer" : "";
  }

  return (
    <>
      <div className="lf-stage lf-stage-studio">
        {name}
        <div className="lf-object lf-studio" ref={boxRef} onClick={onClick} onPointerMove={onPointerMove}>
          {/* eslint-disable-next-line @next/next/no-img-element -- art-directed srcset, not next/image */}
          <img
            src="/studio/studio-1200.webp"
            srcSet={WIDTHS.map((w) => `/studio/studio-${w}.webp ${w}w`).join(", ")}
            sizes="(max-width: 760px) 96vw, 80vw"
            width={FRAME.w}
            height={FRAME.h}
            alt="A studio set out on the blue ground: the gold folding screen, a potted monstera, a desk with three monitors showing Prompt Beach, a code editor and Switchboard, a computer with lit fans, a plush capybara in a scarf, a coffee tray, a stack of books with a camera on top, maracas, a conga, and an easel holding an unfinished abstract painting, a palette at its foot."
            fetchPriority="high"
            draggable={false}
          />
          <Layer name="keys" glow ref={(el) => void (layers.current.keys = el)} />
          <Layer name="conga" ref={(el) => void (layers.current.conga = el)} />
          <Layer name="maracas" ref={(el) => void (layers.current.maracas = el)} />
          {THINGS.map((t) => (
            <button
              key={t}
              type="button"
              className="lf-hit"
              aria-label={LABEL[t]}
              style={at(TARGETS[t])}
              onClick={(e) => {
                e.stopPropagation();
                act(t);
              }}
            />
          ))}
        </div>
      </div>
      <div className="lf-foot lf-foot-studio">{intro}</div>
    </>
  );
}
