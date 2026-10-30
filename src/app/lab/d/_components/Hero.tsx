"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { person } from "@/lab/content";
import { areas, type AreaId } from "../_data";
import CommandPalette from "./CommandPalette";
import WindPortrait from "./WindPortrait";

type Ground = "blue" | "red";

const EDGE: Record<AreaId, string> = {
  fullstack: "left",
  web3: "top",
  mobile: "right",
  ai: "bottom",
};

// Sizes the backdrop word to its zone. At rest the surname overscales so it bleeds
// past both edges; an area word fits its zone and is capped by the zone's height.
function useFitWord(text: string, bleed: number) {
  const ref = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const fit = () => {
      const zone = el.parentElement!;
      el.style.fontSize = "100px";
      const byWidth = (100 * zone.clientWidth) / el.scrollWidth;
      el.style.fontSize = `${Math.min(byWidth * bleed, zone.clientHeight * 1.32)}px`;
    };
    fit();
    const ro = new ResizeObserver(fit);
    ro.observe(el.parentElement!);
    document.fonts?.ready.then(fit);
    return () => ro.disconnect();
  }, [text, bleed]);
  return ref;
}

export default function Hero({ ground, onGround }: { ground: Ground; onGround: (g: Ground) => void }) {
  const [active, setActive] = useState<AreaId | null>(null);
  const area = areas.find((a) => a.id === active) ?? null;
  const giant = area?.giant ?? "BONETE";
  const giantRef = useFitWord(giant, area ? 1 : 1.08);
  const stageRef = useRef<HTMLDivElement>(null);
  const dropRef = useRef<HTMLDivElement>(null);
  const drag = useRef<{ id: AreaId; x: number; y: number; moved: boolean; el: HTMLElement } | null>(null);
  const suppressClick = useRef(false);
  const [dragging, setDragging] = useState<AreaId | null>(null);
  const [over, setOver] = useState(false);

  // Layered depth: the stage publishes the pointer position; layers read it in CSS.
  useEffect(() => {
    const stage = stageRef.current;
    if (!stage || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let raf = 0;
    const move = (e: PointerEvent) => {
      if (e.pointerType !== "mouse") return;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const r = stage.getBoundingClientRect();
        stage.style.setProperty("--px", ((e.clientX - r.left) / r.width - 0.5).toFixed(3));
        stage.style.setProperty("--py", ((e.clientY - r.top) / r.height - 0.5).toFixed(3));
      });
    };
    stage.addEventListener("pointermove", move);
    return () => {
      stage.removeEventListener("pointermove", move);
      cancelAnimationFrame(raf);
    };
  }, []);

  const insideDrop = (x: number, y: number) => {
    const r = dropRef.current?.getBoundingClientRect();
    return !!r && x > r.left && x < r.right && y > r.top && y < r.bottom;
  };

  const onPointerDown = useCallback((e: React.PointerEvent<HTMLButtonElement>, id: AreaId) => {
    if (e.pointerType !== "mouse" || e.button !== 0) return;
    drag.current = { id, x: e.clientX, y: e.clientY, moved: false, el: e.currentTarget };
    e.currentTarget.setPointerCapture(e.pointerId);
  }, []);

  const onPointerMove = useCallback((e: React.PointerEvent<HTMLButtonElement>) => {
    const d = drag.current;
    if (!d) return;
    const dx = e.clientX - d.x;
    const dy = e.clientY - d.y;
    if (!d.moved && Math.hypot(dx, dy) < 6) return;
    if (!d.moved) {
      d.moved = true;
      d.el.style.transition = "none";
      setDragging(d.id);
    }
    d.el.style.translate = `${dx}px ${dy}px`;
    setOver(insideDrop(e.clientX, e.clientY));
  }, []);

  const onPointerUp = useCallback((e: React.PointerEvent<HTMLButtonElement>) => {
    const d = drag.current;
    drag.current = null;
    if (!d) return;
    // Hand the token back to its CSS transition so it glides home.
    d.el.style.transition = "";
    void d.el.offsetWidth;
    d.el.style.translate = "";
    setDragging(null);
    setOver(false);
    if (d.moved) {
      suppressClick.current = true;
      if (insideDrop(e.clientX, e.clientY)) setActive(d.id);
    }
  }, []);

  const onClick = (id: AreaId) => {
    // A drag ends with a click event too; only a genuine click (or keyboard) toggles.
    if (suppressClick.current) {
      suppressClick.current = false;
      return;
    }
    setActive((cur) => (cur === id ? null : id));
  };

  return (
    <section className="ld-hero" aria-labelledby="ld-name">
      <div
        ref={stageRef}
        className="ld-stage"
        data-active={active ?? undefined}
        data-dragging={dragging ? "" : undefined}
        data-over={over ? "" : undefined}
      >
        <div className="ld-giant-wrap" aria-hidden>
          <div ref={giantRef} className="ld-giant" key={giant}>
            {giant}
          </div>
        </div>

        <div ref={dropRef} className="ld-drop" aria-hidden />

        <WindPortrait className="ld-portrait" />

        <header className="ld-top">
          <nav aria-label="Primary" className="ld-nav">
            <a href="#projects">Work</a>
            <a href="/cv.pdf" target="_blank" rel="noreferrer">
              CV
            </a>
            <a href={person.links.github} target="_blank" rel="noreferrer" className="ld-nav-wide">
              GitHub
            </a>
            <a href={person.links.linkedin} target="_blank" rel="noreferrer">
              LinkedIn
            </a>
          </nav>
          <div className="ld-ground" role="group" aria-label="Ground colour (preview)">
            <button type="button" aria-pressed={ground === "blue"} onClick={() => onGround("blue")}>
              Añil
            </button>
            <button type="button" aria-pressed={ground === "red"} onClick={() => onGround("red")}>
              Almagre
            </button>
          </div>
          <div className="ld-cmd">
            <CommandPalette />
          </div>
        </header>

        <div className="ld-intro">
          <div className="ld-id">
            <h1 id="ld-name">Maria Bonete</h1>
            <p className="ld-role">
              Developer in Spain, shipping across four areas with equal weight: full-stack web,
              mobile, Web3 and AI-driven engineering.
            </p>
            {!area && (
              <p className="ld-hint">
                <span className="ld-hint-fine">Pull an area into the frame</span>
                <span className="ld-hint-coarse">Tap an area</span> to see the proof behind it.
              </p>
            )}
          </div>

          <div className="ld-proof" aria-live="polite">
            {area && (
              <>
                <div className="ld-proof-head">
                  <h2>{area.label}</h2>
                  <button type="button" className="ld-link" onClick={() => setActive(null)}>
                    Back to Maria
                  </button>
                </div>
                <ul>
                  {area.proof.map((p) => (
                    <li key={p.title}>
                      {p.href ? (
                        <a href={p.href} {...(p.href.startsWith("http") ? { target: "_blank", rel: "noreferrer" } : {})}>
                          {p.title}
                        </a>
                      ) : (
                        <strong>{p.title}</strong>
                      )}
                      <span>{p.fact}</span>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>

          <div className="ld-actions">
            <a className="ld-primary" href="#projects">
              See the work
            </a>
            <a className="ld-link ld-plate" href="/cv.pdf" target="_blank" rel="noreferrer">
              CV (PDF)
            </a>
          </div>
        </div>

        <ul className="ld-tokens" aria-label="Areas">
          {areas.map((a) => (
            <li key={a.id} data-edge={EDGE[a.id]}>
              <button
                type="button"
                className="ld-token"
                aria-pressed={active === a.id}
                data-dragging={dragging === a.id || undefined}
                onPointerDown={(e) => onPointerDown(e, a.id)}
                onPointerMove={onPointerMove}
                onPointerUp={onPointerUp}
                onPointerCancel={onPointerUp}
                onClick={() => onClick(a.id)}
              >
                {a.label}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
