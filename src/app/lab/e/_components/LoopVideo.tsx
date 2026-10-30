"use client";

import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "./lightStore";

type Props = { src: string; poster: string; width: number; height: number; label: string };

// A looping clip with its own pause control: motion that runs past five seconds must be stoppable.
// It plays only on screen, and under reduced motion it rests on its poster until asked to play.
export default function LoopVideo({ src, poster, width, height, label }: Props) {
  const ref = useRef<HTMLVideoElement>(null);
  const reduced = useReducedMotion();
  const [chosen, setChosen] = useState<boolean | null>(null);
  const [inView, setInView] = useState(false);
  const playing = chosen ?? !reduced;

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setInView(e.isIntersecting), { rootMargin: "200px 0px" });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    if (playing && inView) v.play().catch(() => {});
    else v.pause();
  }, [playing, inView]);

  return (
    <>
      <video
        ref={ref}
        src={src}
        poster={poster}
        width={width}
        height={height}
        muted
        loop
        playsInline
        preload="none"
        aria-label={label}
      />
      <button
        type="button"
        className="le-clip-toggle"
        aria-label={playing ? "Pause the clip" : "Play the clip"}
        onClick={() => setChosen(!playing)}
      >
        <svg viewBox="0 0 12 12" aria-hidden>
          {playing ? <path d="M3 2.2h1.6v7.6H3zM7.4 2.2H9v7.6H7.4z" /> : <path d="M3.4 1.9 10 6l-6.6 4.1z" />}
        </svg>
      </button>
    </>
  );
}
