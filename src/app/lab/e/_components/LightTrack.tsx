"use client";

import { useEffect, useRef } from "react";
import { LIGHTS, describe, light, usePlaying } from "./lightStore";

const STEP = 0.125; // arrow keys move an eighth of a light

// A thin line coloured like the day's light with a marker riding on it. Drag or click to set the
// light (which pauses the flow); the mark beside it pauses and resumes.
export default function LightTrack() {
  const trackRef = useRef<HTMLSpanElement>(null);
  const markerRef = useRef<HTMLSpanElement>(null);
  const playing = usePlaying();

  useEffect(
    () =>
      light.onFrame((p) => {
        markerRef.current?.style.setProperty("--at", `${(p / LIGHTS.length) * 100}%`);
        const t = trackRef.current;
        if (t) {
          // Only touch the ARIA values when they change, so a focused slider is not re-announced every frame.
          const now = ((p / LIGHTS.length) * 100).toFixed(0);
          const text = describe(p);
          if (t.getAttribute("aria-valuenow") !== now) t.setAttribute("aria-valuenow", now);
          if (t.getAttribute("aria-valuetext") !== text) t.setAttribute("aria-valuetext", text);
        }
      }),
    [],
  );

  const setFromPointer = (clientX: number) => {
    const r = trackRef.current!.getBoundingClientRect();
    const x = Math.min(Math.max((clientX - r.left) / r.width, 0), 0.9999);
    light.setPosition(x * LIGHTS.length);
  };

  const onPointerDown = (e: React.PointerEvent<HTMLSpanElement>) => {
    e.currentTarget.setPointerCapture(e.pointerId);
    light.setPlaying(false);
    setFromPointer(e.clientX);
  };
  const onPointerMove = (e: React.PointerEvent<HTMLSpanElement>) => {
    if (e.currentTarget.hasPointerCapture(e.pointerId)) setFromPointer(e.clientX);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    const p = light.position;
    const moves: Record<string, number> = {
      ArrowRight: p + STEP,
      ArrowUp: p + STEP,
      ArrowLeft: p - STEP,
      ArrowDown: p - STEP,
      PageUp: Math.floor(p) + 1,
      PageDown: Math.ceil(p) - 1,
      Home: 0,
      End: LIGHTS.length - 1,
    };
    if (!(e.key in moves)) return;
    e.preventDefault();
    light.setPlaying(false);
    light.setPosition(moves[e.key]);
  };

  return (
    <span className="le-light">
      <span
        ref={trackRef}
        className="le-track"
        role="slider"
        tabIndex={0}
        aria-label="Light on the screen"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={0}
        aria-valuetext="Gold"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onKeyDown={onKeyDown}
      >
        <span ref={markerRef} className="le-marker" aria-hidden />
      </span>
      <button
        type="button"
        className="le-playpause"
        aria-label={playing ? "Pause the light" : "Play the light"}
        onClick={() => light.setPlaying(!playing)}
      >
        <svg viewBox="0 0 12 12" aria-hidden>
          {playing ? (
            <path d="M3 2.2h1.6v7.6H3zM7.4 2.2H9v7.6H7.4z" />
          ) : (
            <path d="M3.4 1.9 10 6l-6.6 4.1z" />
          )}
        </svg>
      </button>
    </span>
  );
}
