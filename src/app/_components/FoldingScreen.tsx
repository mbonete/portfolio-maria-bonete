"use client";

import { useEffect, useRef, type ReactNode } from "react";

const ALT = {
  open: "A four-panel gold-leaf folding screen standing open on the blue ground. Maria's profile shadow, chin lifted and hair loose, falls across the second panel beside a painted violet stream; an ink plum branch in bloom crosses the last two.",
  shut: "A four-panel gold-leaf folding screen, folded nearly shut, standing on the blue ground.",
};

// The renders: N frames from nearly shut to open. A click plays them one way or the other.
const N = 28;
const MS = 650;
const HOLD = 1000; // how long it rests shut when the page opens
const pad = (k: number) => String(k).padStart(2, "0");
const clamp = (v: number) => Math.min(Math.max(v, 0), 1);
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);

type Rest = "shut" | "open";

// The screen at rest, at full size: the shut and open frames, each a back and a front plate.
function Still({ rest, front }: { rest: Rest; front?: boolean }) {
  const name = front ? `${rest}-front` : rest;
  return (
    // eslint-disable-next-line @next/next/no-img-element -- art-directed srcset, not next/image
    <img
      className={`lf-still lf-${rest}`}
      src={`/fold/${name}-1180.webp`}
      srcSet={[1180, 1770, 2360].map((w) => `/fold/${name}-${w}.webp ${w}w`).join(", ")}
      sizes="(max-width: 760px) 96vw, 80vw"
      width={2360}
      height={1322}
      alt={front ? "" : ALT[rest]}
      aria-hidden={front || undefined}
      fetchPriority={rest === "shut" ? "high" : undefined}
      draggable={false}
    />
  );
}

// The screen on its ground, the name threaded through its folds: the two panels folding toward the
// viewer stand in front of the letters, the others behind. It arrives shut and opens by itself a
// moment later; from then on a click or tap on it (or, from the keyboard, the hidden button) folds
// it shut or opens it. It never stops in between.
//
// The stage's data-state says what shows: "arriving" (server markup: the shut still, or the open
// one without script or with reduced motion), "shut" or "open" (that still), "moving" (the renders,
// played on two canvases). Each switch to "moving" paints the canvas first, so nothing blinks.
export default function FoldingScreen({ name, intro }: { name: ReactNode; intro: ReactNode }) {
  const stageRef = useRef<HTMLDivElement>(null);
  const backRef = useRef<HTMLCanvasElement>(null);
  const frontRef = useRef<HTMLCanvasElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const stage = stageRef.current;
    const object = stage?.querySelector<HTMLElement>(".lf-object");
    const canvases = [backRef.current, frontRef.current];
    const button = buttonRef.current;
    if (!stage || !object || !button || !canvases[0] || !canvases[1]) return;
    const ctx = canvases.map((c) => c!.getContext("2d")!);
    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const set = (state: Rest | "moving") => (stage.dataset.state = state);
    const stills = (rest: Rest) => [...stage.querySelectorAll<HTMLImageElement>(`.lf-${rest}`)];

    let open = reduced;
    let shown = open ? 1 : 0; // 0 shut, 1 open
    let raf = 0;
    let ready = false;
    let touched = false; // the visitor has folded it themselves
    let frames: HTMLImageElement[][] = []; // [back, front], each N renders
    set(open ? "open" : "shut");
    button.textContent = open ? "Fold the screen shut" : "Open the screen";

    const paint = () => {
      // Between two renders, a cross-fade in premultiplied light ("lighter" adds them).
      const x = clamp(shown) * (N - 1);
      const k = Math.min(Math.floor(x), N - 1);
      const f = x - k;
      frames.forEach((stack, s) => {
        const c = ctx[s];
        c.globalCompositeOperation = "source-over";
        c.globalAlpha = 1;
        c.clearRect(0, 0, c.canvas.width, c.canvas.height);
        c.globalCompositeOperation = "lighter";
        c.globalAlpha = 1 - f;
        c.drawImage(stack[k], 0, 0, c.canvas.width, c.canvas.height);
        if (f > 0.002 && k + 1 < N) {
          c.globalAlpha = f;
          c.drawImage(stack[k + 1], 0, 0, c.canvas.width, c.canvas.height);
        }
      });
    };

    const go = (toOpen: boolean) => {
      open = toOpen;
      button.textContent = open ? "Fold the screen shut" : "Open the screen";
      cancelAnimationFrame(raf);
      const from = shown;
      const to = open ? 1 : 0;
      const rest = () => {
        shown = to;
        raf = 0;
        set(open ? "open" : "shut");
      };
      // A reversal mid-way takes only the time left to cover.
      const ms = reduced ? 0 : MS * Math.abs(to - from);
      if (!ms) return rest();
      paint();
      set("moving");
      const t0 = performance.now();
      const step = (now: number) => {
        const t = clamp((now - t0) / ms);
        shown = from + (to - from) * ease(t);
        paint();
        if (t < 1) raf = requestAnimationFrame(step);
        else rest();
      };
      raf = requestAnimationFrame(step);
    };
    const toggle = () => {
      if (!ready) return;
      touched = true;
      go(!open);
    };

    // Everything the motion needs, decoded before it starts: the renders, and both stills it ends on.
    let cancelled = false;
    let timer = 0;
    const load = (src: string) =>
      new Promise<HTMLImageElement>((resolve, reject) => {
        const img = new Image();
        img.onload = () => img.decode().then(() => resolve(img), () => resolve(img));
        img.onerror = reject;
        img.src = src;
      });
    const decode = (imgs: HTMLImageElement[]) => Promise.all(imgs.map((img) => img.decode().catch(() => {})));
    const held = decode(stills("shut")).then(() => new Promise((r) => (timer = window.setTimeout(r, HOLD))));
    Promise.all([
      Promise.all(["b", "f"].map((s) => Promise.all(Array.from({ length: N }, (_, k) => load(`/fold/${s}-${pad(k)}.webp`))))),
      decode([...stills("open"), ...stills("shut")]),
      reduced ? null : held,
    ]).then(
      ([stacks]) => {
        if (cancelled) return;
        canvases.forEach((c) => {
          c!.width = stacks[0][0].naturalWidth;
          c!.height = stacks[0][0].naturalHeight;
        });
        frames = stacks;
        ready = true;
        stage.setAttribute("data-ready", "");
        button.disabled = false;
        if (!open && !touched) go(true);
      },
      () => {
        if (cancelled) return;
        open = true; // without the renders it simply stands open
        set("open");
      },
    );

    object.addEventListener("click", toggle);
    button.addEventListener("click", toggle);
    return () => {
      cancelled = true;
      cancelAnimationFrame(raf);
      clearTimeout(timer);
      object.removeEventListener("click", toggle);
      button.removeEventListener("click", toggle);
    };
  }, []);

  return (
    <>
      <div ref={stageRef} className="lf-stage" data-state="arriving">
        {name}
        <noscript>
          <style>{".lf-stage .lf-shut { visibility: hidden !important; } .lf-stage .lf-open { visibility: visible !important; }"}</style>
        </noscript>
        <div className="lf-object">
          <Still rest="shut" />
          <Still rest="open" />
          <canvas ref={backRef} className="lf-seq" aria-hidden />
        </div>
        <div className="lf-object lf-object-front" aria-hidden>
          <Still rest="shut" front />
          <Still rest="open" front />
          <canvas ref={frontRef} className="lf-seq" />
        </div>
      </div>
      <div className="lf-foot">
        {intro}
        <button ref={buttonRef} type="button" className="lf-sr lf-fold" disabled>
          Open the screen
        </button>
      </div>
    </>
  );
}
