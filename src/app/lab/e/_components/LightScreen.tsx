"use client";

import { useEffect, useRef, useState } from "react";
import { LIGHTS, MS_PER_LIGHT, accentAt, light, usePlaying } from "./lightStore";

const ALT =
  "Maria's profile shadow, chin lifted and long hair loose, falls across a four-panel gold-leaf screen beside a painted violet stream; an old plum tree in ink, in bloom, rises across the far panels.";

// The same render of the screen under four lamps. Between two lights, the next render sits on top of
// the current one at the in-between opacity, so the colour flows like a string of fading lights.
// `echo` is the same screen seen again at the end of the page: decorative, and sharing the one light.
export default function LightScreen({ echo = false }: { echo?: boolean }) {
  const rootRef = useRef<HTMLDivElement>(null);
  const plates = useRef<(HTMLElement | null)[]>([]);
  const playing = usePlaying();
  const [inView, setInView] = useState(true);

  // Paint every position change: layer opacities and the page's accent.
  useEffect(() => {
    const page = rootRef.current?.closest<HTMLElement>(".le");
    let accent = "";
    return light.onFrame((p) => {
      const i = Math.floor(p) % LIGHTS.length;
      const next = (i + 1) % LIGHTS.length;
      const f = p - Math.floor(p);
      plates.current.forEach((el, k) => {
        if (!el) return;
        const on = k === i || k === next;
        el.style.visibility = on ? "visible" : "hidden";
        el.style.zIndex = k === next ? "1" : "0";
        el.style.opacity = k === next ? f.toFixed(4) : "1";
      });
      // The accent restyles the whole page, so it steps in 32nds of a light (about 13 writes a
      // second while flowing) and is written only when it actually changes.
      const next_ = accentAt(Math.round(p * 32) / 32);
      if (next_ !== accent) {
        accent = next_;
        page?.style.setProperty("--accent", accent);
      }
    });
  }, []);

  // Flow at a constant speed while playing and on screen.
  useEffect(() => {
    if (!playing || !inView) return;
    let raf = 0;
    let last = performance.now();
    const tick = (now: number) => {
      light.setPosition(light.position + (now - last) / MS_PER_LIGHT);
      last = now;
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing, inView]);

  useEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setInView(e.isIntersecting));
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div ref={rootRef} className="le-plates">
      {LIGHTS.map((l, i) => (
        <picture
          key={l.id}
          ref={(el) => {
            plates.current[i] = el;
          }}
          className="le-plate"
        >
          <source
            media="(max-aspect-ratio: 4/5)"
            srcSet={`/lab/e/light-${l.id}-m780.webp 780w, /lab/e/light-${l.id}-m1170.webp 1170w, /lab/e/light-${l.id}-m1560.webp 1560w`}
            sizes="100vw"
          />
          <img
            src={`/lab/e/light-${l.id}-1600.webp`}
            srcSet={`/lab/e/light-${l.id}-1600.webp 1600w, /lab/e/light-${l.id}-2560.webp 2560w, /lab/e/light-${l.id}-2880.webp 2880w, /lab/e/light-${l.id}-3840.webp 3840w`}
            sizes="100vw"
            alt={i === 0 && !echo ? ALT : ""}
            aria-hidden={i === 0 && !echo ? undefined : true}
            fetchPriority={i === 0 && !echo ? "high" : "low"}
            loading={echo ? "lazy" : undefined}
            decoding="async"
          />
        </picture>
      ))}
    </div>
  );
}
