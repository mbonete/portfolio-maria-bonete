"use client";

import { createContext, useContext, useEffect, useId, useRef, useState } from "react";

// A band's demo: a play button on the band's screens starts it in their place, and while it plays a
// "Close the video" control sits with the band's links. Only one plays at a time: starting one closes
// any other.
type Video = { playing: boolean; play: () => void; close: () => void };

const VideoContext = createContext<Video | null>(null);

export function useBandVideo() {
  return useContext(VideoContext);
}

export function BandVideo({ children }: { children: React.ReactNode }) {
  const id = useId();
  const [playing, setPlaying] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const closedByHand = useRef(false);

  // Another band's video starting closes this one.
  useEffect(() => {
    const onPlay = (e: Event) => {
      if ((e as CustomEvent<string>).detail !== id) setPlaying(false);
    };
    addEventListener("lf-video-play", onPlay);
    return () => removeEventListener("lf-video-play", onPlay);
  }, [id]);

  // Keyboard focus follows the swap: into the player when it opens, and back to the play button when
  // it's closed by hand (not when another video took over, which has the focus now).
  useEffect(() => {
    if (playing) root.current?.querySelector<HTMLIFrameElement>("iframe")?.focus();
    else if (closedByHand.current) root.current?.querySelector<HTMLButtonElement>(".lf-poster-play")?.focus();
    closedByHand.current = false;
  }, [playing]);

  const play = () => {
    dispatchEvent(new CustomEvent("lf-video-play", { detail: id }));
    setPlaying(true);
  };
  const close = () => {
    closedByHand.current = true;
    setPlaying(false);
  };

  return (
    <VideoContext.Provider value={{ playing, play, close }}>
      <div ref={root} className="lf-band-video">
        {children}
      </div>
    </VideoContext.Provider>
  );
}

// The play button over the screens.
export function PosterPlay({ label }: { label: string }) {
  const video = useBandVideo();
  if (!video || video.playing) return null;
  return (
    <button type="button" className="lf-poster-play" aria-label={label} onClick={video.play}>
      <span aria-hidden />
    </button>
  );
}

export function CloseVideo() {
  const video = useBandVideo();
  if (!video?.playing) return null;
  return (
    <button type="button" className="lf-play-toggle" onClick={video.close}>
      Close the video
    </button>
  );
}
