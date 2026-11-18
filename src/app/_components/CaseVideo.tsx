"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

const ext = { target: "_blank", rel: "noreferrer" } as const;
const time = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

// A case study's video, the same on every case study: the play button leads the head's links, so it
// shows in the first screen, and the poster below takes the whole width (a web project's inside its
// browser window, as on its home band). Pressing either swaps the poster for YouTube's own player, with
// its controls and fullscreen, and moves focus into it. Nothing from YouTube (or its cookies) loads
// before that.
export default function CaseVideo({
  id,
  title,
  label,
  seconds,
  poster,
  browser,
  url,
  children,
}: {
  id: string;
  title: string;
  label: string; // "Play the trailer", "Play the demo"
  seconds: number;
  poster: ReactNode;
  browser?: boolean; // a web project: the poster sits in a browser window
  url?: string; // its public address for the window's bar, when it has one
  children?: ReactNode; // the head's other links
}) {
  const [playing, setPlaying] = useState(false);
  const frame = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (playing) frame.current?.focus();
  }, [playing]);

  const video = (
    <div className="lf-cs-video">
      {playing ? (
        <iframe
          ref={frame}
          src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&playsinline=1`}
          title={title}
          allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
          allowFullScreen
        />
      ) : (
        // A larger target for the same action; keyboard and screen readers use the button above.
        <div className="lf-cs-poster" onClick={() => setPlaying(true)} aria-hidden>
          {poster}
          <span className="lf-cs-poster-cue" />
        </div>
      )}
    </div>
  );

  return (
    <>
      <p className="lf-cs-links">
        {!playing && (
          <button type="button" className="lf-cs-play" onClick={() => setPlaying(true)}>
            {label} <span className="lf-cs-play-time">{time(seconds)}</span>
          </button>
        )}
        <a href={`https://www.youtube.com/watch?v=${id}`} {...ext}>
          Watch it on YouTube
        </a>
        {children}
      </p>
      {browser ? (
        <div className="lf-browser lf-cs-window">
          <div className="lf-browser-bar" aria-hidden>
            <span className="lf-browser-dots" />
            {url && <span className="lf-browser-url">{url}</span>}
          </div>
          {video}
        </div>
      ) : (
        video
      )}
    </>
  );
}
