"use client";

import { useEffect, useRef, type ReactNode } from "react";

const ALT =
  "A four-panel gold-leaf folding screen standing open on the blue ground. Maria's profile shadow, chin lifted and hair loose, falls across the second panel beside a painted violet stream; an ink plum branch in bloom crosses the last two.";

// The renders: N frames from nearly shut to open. A click plays them one way or the other.
const N = 28;
const MS = 650;
const pad = (k: number) => String(k).padStart(2, "0");
const clamp = (v: number) => Math.min(Math.max(v, 0), 1);
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);

function Open({ front }: { front?: boolean }) {
  const name = front ? "open-front" : "open";
  return (
    // eslint-disable-next-line @next/next/no-img-element -- art-directed srcset, not next/image
    <img
      className="lf-open"
      src={`/lab/f/fold/${name}-1180.webp`}
      srcSet={[1180, 1770, 2360].map((w) => `/lab/f/fold/${name}-${w}.webp ${w}w`).join(", ")}
      sizes="(max-width: 760px) 96vw, 80vw"
      width={2360}
      height={1322}
      alt={front ? "" : ALT}
      aria-hidden={front || undefined}
      fetchPriority="high"
      decoding="async"
      draggable={false}
    />
  );
}

// The screen on its ground, the name threaded through its folds: the two panels folding toward the
// viewer stand in front of the letters, the others behind. A click or tap on it (or the caption's
// button) folds it shut or opens it; it never stops in between.
export default function FoldingScreen({ name, intro }: { name: ReactNode; intro: ReactNode }) {
  const stageRef = useRef<HTMLDivElement>(null);
  const backRef = useRef<HTMLCanvasElement>(null);
  const frontRef = useRef<HTMLCanvasElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const cueRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const stage = stageRef.current;
    const object = stage?.querySelector<HTMLElement>(".lf-object");
    const canvases = [backRef.current, frontRef.current];
    const button = buttonRef.current;
    const cue = cueRef.current;
    if (!stage || !object || !button || !cue || !canvases[0] || !canvases[1]) return;
    const ctx = canvases.map((c) => c!.getContext("2d")!);
    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

    let shown = 1; // 0 shut, 1 open
    let open = true;
    let raf = 0;
    let frames: HTMLImageElement[][] | null = null; // [back, front], each N renders

    const paint = () => {
      const moving = shown < 0.999;
      stage.toggleAttribute("data-moving", moving);
      if (!moving || !frames) return;
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

    const toggle = () => {
      if (!frames) return;
      open = !open;
      const word = open ? "fold it" : "open it";
      cue.textContent = `Click the screen to ${word}`;
      button.textContent = open ? "Fold the screen shut" : "Open the screen";
      cancelAnimationFrame(raf);
      const from = shown;
      const to = open ? 1 : 0;
      // A reversal mid-way takes only the time left to cover.
      const ms = reduced ? 0 : MS * Math.abs(to - from);
      const t0 = performance.now();
      const step = (now: number) => {
        const t = ms ? clamp((now - t0) / ms) : 1;
        shown = from + (to - from) * ease(t);
        paint();
        raf = t < 1 ? requestAnimationFrame(step) : 0;
      };
      raf = requestAnimationFrame(step);
    };

    let cancelled = false;
    const load = (src: string) =>
      new Promise<HTMLImageElement>((resolve, reject) => {
        const img = new Image();
        img.decoding = "async";
        img.onload = () => img.decode().then(() => resolve(img), () => resolve(img));
        img.onerror = reject;
        img.src = src;
      });
    const start = () =>
      Promise.all(
        ["b", "f"].map((s) => Promise.all(Array.from({ length: N }, (_, k) => load(`/lab/f/fold/${s}-${pad(k)}.webp`)))),
      ).then(
        (stacks) => {
          if (cancelled) return;
          frames = stacks;
          canvases.forEach((c) => {
            c!.width = stacks[0][0].naturalWidth;
            c!.height = stacks[0][0].naturalHeight;
          });
          stage.setAttribute("data-ready", "");
          button.disabled = false;
        },
        () => {}, // without the renders the screen simply stays open
      );
    if (document.readyState === "complete") start();
    else addEventListener("load", start, { once: true });

    object.addEventListener("click", toggle);
    button.addEventListener("click", toggle);
    return () => {
      cancelled = true;
      cancelAnimationFrame(raf);
      removeEventListener("load", start);
      object.removeEventListener("click", toggle);
      button.removeEventListener("click", toggle);
    };
  }, []);

  return (
    <>
      <div ref={stageRef} className="lf-stage">
        {name}
        <div className="lf-object">
          <Open />
          <canvas ref={backRef} className="lf-seq" aria-hidden />
        </div>
        <div className="lf-object lf-object-front" aria-hidden>
          <Open front />
          <canvas ref={frontRef} className="lf-seq" />
        </div>
      </div>
      <div className="lf-foot">
        {intro}
        <div className="lf-caption">
          <p className="lf-caption-title">Folding screen in four panels</p>
          <p>Gold leaf, ink and the shadow of her profile. Modelled and rendered in Blender.</p>
          <p className="lf-fold">
            <span ref={cueRef} className="lf-fold-cue">
              Click the screen to fold it
            </span>
            <button ref={buttonRef} type="button" className="lf-sr" disabled>
              Fold the screen shut
            </button>
          </p>
        </div>
      </div>
    </>
  );
}
