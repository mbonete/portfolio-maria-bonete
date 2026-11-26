"use client";

import { useEffect, useRef, type MouseEvent, type PointerEvent as PointerEventR, type ReactNode } from "react";
import { BREEZE, CUTOUTS, FLASH_HEAD, FRAME, HIT, LIGHTS, SWAPS, TARGETS } from "./studio-layers";

// The hero's object: the studio, rendered in Blender (tools/studio), on the blue ground under the
// name. Eight things in it answer a click or tap, each with a sound: the conga gives a hit, the maracas
// a shake, the plush capybara a squeak as it squashes, the keyboard a burst of typing while its LEDs
// flare, the camera a shot with its flash, the computer's LEDs change colour, the painting on the easel
// moves on a stage, and a breeze goes through the monstera.
//
// The studio is a stack of renders from one camera (tools/studio/layers.py): the room without the
// things that move; the painting's stages and the computer's colours, each shown in place over it; the
// LEDs' and the flash's light, added on top; and the moving things cut out, each over its place.
// A quarter-size map of the silhouettes (hit.png) says what a click landed on: anything within REACH px
// of a silhouette counts, more so with a finger. From the keyboard, each thing has a button of its own.

type Thing = keyof typeof HIT;
const THINGS = Object.keys(HIT) as Thing[];
const BY_GREY = Object.fromEntries(Object.entries(HIT).map(([t, n]) => [n, t])) as Record<number, Thing>;
const LABEL: Record<Thing, string> = {
  conga: "Play the conga",
  maracas: "Shake the maracas",
  keys: "Type on the keyboard",
  capybara: "Squeeze the capybara",
  camera: "Take a photo with the camera",
  tower: "Change the colour of the computer's lights",
  easel: "Paint the next stage of the painting",
  monstera: "Send a breeze through the monstera",
};
const WIDTHS = [1200, 1800, 2400];
const REACH = { mouse: 18, touch: 30 }; // CSS px around each silhouette
type Box = { x: number; y: number; w: number; h: number };
const pct = (v: number, of: number) => `${((100 * v) / of).toFixed(4)}%`;
const at = (b: Box) => ({ left: pct(b.x, FRAME.w), top: pct(b.y, FRAME.h), width: pct(b.w, FRAME.w), height: pct(b.h, FRAME.h) });

// Moves, as keyframes for the Web Animations API, on the element the thing shows in. Reduced motion
// keeps every sound, the light (as a plain rise and fall) and the swaps, and drops the movement.
const MOVES: Partial<Record<Thing, { frames: Keyframe[]; ms: number; still?: Keyframe[]; easing?: string }>> = {
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
  // squeezed from above, it spreads, springs back up and settles
  capybara: {
    frames: [
      { transform: "none" },
      { transform: "scale(1.05, 0.9)", offset: 0.2 },
      { transform: "scale(0.98, 1.035)", offset: 0.48 },
      { transform: "scale(1.01, 0.99)", offset: 0.72 },
      { transform: "none" },
    ],
    ms: 560,
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
    easing: "linear",
  },
  // the flash's light on what is in front of it, in at once, out over a third of a second
  camera: {
    frames: [{ opacity: 0 }, { opacity: 1, offset: 0.04 }, { opacity: 0.8, offset: 0.2 }, { opacity: 0 }],
    ms: 420,
    still: [{ opacity: 0 }, { opacity: 1, offset: 0.04 }, { opacity: 0.8, offset: 0.2 }, { opacity: 0 }],
    easing: "ease-out",
  },
};
const BURST: Keyframe[] = [
  { opacity: 0, transform: "translate(-50%, -50%) scale(0.3)" },
  { opacity: 1, transform: "translate(-50%, -50%) scale(1)", offset: 0.08 },
  { opacity: 0, transform: "translate(-50%, -50%) scale(1.6)" },
];

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

// One layer of the stack, placed over its box in the frame.
function Layer({ name, box, className = "", ref }: { name: string; box: Box; className?: string; ref?: (el: HTMLImageElement | null) => void }) {
  const f = box.w / FRAME.w;
  return (
    // eslint-disable-next-line @next/next/no-img-element -- art-directed srcset, not next/image
    <img
      ref={ref}
      className={`lf-layer ${className}`}
      src={`/studio/${name}-1200.webp`}
      srcSet={WIDTHS.map((s) => `/studio/${name}-${s}.webp ${Math.round((box.w * s) / FRAME.w)}w`).join(", ")}
      sizes={`(max-width: 760px) calc(96vw * ${f.toFixed(4)}), calc(80vw * ${f.toFixed(4)})`}
      width={box.w}
      height={box.h}
      style={{ left: pct(box.x, FRAME.w), top: pct(box.y, FRAME.h), width: pct(box.w, FRAME.w) }}
      alt=""
      aria-hidden
      draggable={false}
    />
  );
}

export default function StudioScene({ name, intro }: { name: ReactNode; intro: ReactNode }) {
  const boxRef = useRef<HTMLDivElement>(null);
  const els = useRef<Partial<Record<string, HTMLElement | null>>>({});
  const moving = useRef<Partial<Record<string, Animation>>>({});
  const map = useRef<{ data: Uint8ClampedArray; w: number; h: number } | null>(null);
  const breeze = useRef<ImageBitmap[]>([]);
  const breezing = useRef<Promise<void> | null>(null);
  const swap = useRef({ tower: 0, easel: 0 });
  const keep = (key: string) => (el: HTMLElement | null) => void (els.current[key] = el);

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
      // the breeze's frames (about 600 KB), decoded ahead so the first one plays smoothly; with Data
      // Saver on they wait for the first click on the monstera
      const saveData = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection?.saveData;
      if (!saveData && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) void loadBreeze();
    });
    return () => {
      gone = true;
    };
  }, []);

  function loadBreeze() {
    breezing.current ??= Promise.all(
      Array.from({ length: BREEZE.frames }, (_, k) =>
        fetch(`/studio/monstera-f${String(k + 1).padStart(2, "0")}.webp`)
          .then((r) => r.blob())
          .then((b) => createImageBitmap(b)),
      ),
    ).then((frames) => {
      breeze.current = frames;
    });
    return breezing.current.catch(() => {});
  }

  // What is under, or within `reach` CSS px of, a point: the nearest silhouette (the map already has the
  // nearer thing on top where two overlap).
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
        const t = BY_GREY[Math.round(m.data[(py * m.w + px) * 4] / 30)];
        if (t) {
          best = t;
          bestD = d;
        }
      }
    }
    return best;
  }

  function animate(key: string, frames: Keyframe[], ms: number, easing = "ease-out") {
    const el = els.current[key];
    if (!el) return;
    moving.current[key]?.cancel();
    moving.current[key] = el.animate(frames, { duration: ms, easing });
  }

  // The painting and the computer's lights move one variant on, back to the room's own after the last.
  function next(region: "tower" | "easel") {
    const n = (swap.current[region] = (swap.current[region] + 1) % (SWAPS[region].count + 1));
    for (let k = 1; k <= SWAPS[region].count; k++) {
      const el = els.current[`${region}-${k}`];
      if (el) el.style.opacity = k === n ? "1" : "0";
    }
  }

  // The breeze: the monstera's frames drawn in turn on a canvas over it, then back to the still.
  function blow() {
    const canvas = els.current["monstera-canvas"] as HTMLCanvasElement | null;
    const still = els.current.monstera;
    const frames = breeze.current;
    if (!canvas || !still || !frames.length || canvas.dataset.playing) return;
    canvas.width = frames[0].width;
    canvas.height = frames[0].height;
    const g = canvas.getContext("2d")!;
    let t0 = -1; // the first frame's time
    canvas.dataset.playing = "1";
    const step = (now: number) => {
      if (t0 < 0) t0 = now;
      const k = Math.floor(((now - t0) / 1000) * BREEZE.fps);
      if (k >= frames.length) {
        still.style.visibility = "";
        canvas.style.visibility = "hidden";
        delete canvas.dataset.playing;
        return;
      }
      g.clearRect(0, 0, canvas.width, canvas.height);
      g.drawImage(frames[k], 0, 0);
      if (k === 0) {
        canvas.style.visibility = "visible";
        still.style.visibility = "hidden";
      }
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  function act(t: Thing) {
    play(t);
    const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (t === "tower" || t === "easel") return next(t);
    if (t === "monstera") return still ? undefined : void loadBreeze().then(blow);
    const move = MOVES[t];
    if (!move) return;
    const frames = still ? move.still : move.frames;
    if (frames) animate(t, frames, move.ms, move.easing);
    if (t === "camera" && !still) animate("burst", BURST, 380);
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
      <div className="lf-stage">
        {name}
        <div className="lf-object lf-studio" ref={boxRef} onClick={onClick} onPointerMove={onPointerMove}>
          {/* eslint-disable-next-line @next/next/no-img-element -- art-directed srcset, not next/image */}
          <img
            src="/studio/studio-1200.webp"
            srcSet={WIDTHS.map((w) => `/studio/studio-${w}.webp ${w}w`).join(", ")}
            sizes="(max-width: 760px) 96vw, 80vw"
            width={FRAME.w}
            height={FRAME.h}
            alt="A studio set out on the blue ground: a lacquered folding screen painted on paper with a violet stream and a plum branch, a potted monstera, a desk with three monitors showing Prompt Beach, a code editor and Switchboard, a computer with lit fans, a plush capybara in a scarf, a coffee tray, a stack of books with a camera on top, maracas, a conga, and an easel holding an unfinished abstract painting, a palette at its foot."
            fetchPriority="high"
            draggable={false}
          />
          {(["tower", "easel"] as const).flatMap((r) =>
            Array.from({ length: SWAPS[r].count }, (_, k) => (
              <Layer
                key={`${r}-${k + 1}`}
                name={`${r}-${r === "tower" ? "p" : "s"}${k + 1}`}
                box={SWAPS[r]}
                className="lf-swap"
                ref={keep(`${r}-${k + 1}`)}
              />
            )),
          )}
          <Layer name="keys" box={LIGHTS.keys} className="lf-glow" ref={keep("keys")} />
          <Layer name="flash" box={LIGHTS.flash} className="lf-glow" ref={keep("camera")} />
          <Layer name="monstera" box={CUTOUTS.monstera} ref={keep("monstera")} />
          <canvas
            ref={keep("monstera-canvas")}
            className="lf-layer lf-breeze"
            style={{ ...at(CUTOUTS.monstera), visibility: "hidden" }}
            aria-hidden
          />
          {(["capybara", "conga", "maracas"] as const).map((t) => (
            <Layer key={t} name={t} box={CUTOUTS[t]} className={`lf-layer-${t}`} ref={keep(t)} />
          ))}
          <span
            ref={keep("burst")}
            className="lf-burst"
            style={{ left: pct(FLASH_HEAD.x, FRAME.w), top: pct(FLASH_HEAD.y, FRAME.h) }}
            aria-hidden
          />
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
      <div className="lf-foot">{intro}</div>
    </>
  );
}
