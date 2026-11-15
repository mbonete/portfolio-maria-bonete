"use client";

import Image from "next/image";
import { useState } from "react";

// The trailer as a still until it is asked for: YouTube's player (and its cookies) loads on the click.
export default function Trailer({ id, title, poster }: { id: string; title: string; poster: string }) {
  const [playing, setPlaying] = useState(false);

  return (
    <div className="lf-trailer">
      {playing ? (
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`}
          title={title}
          allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
          allowFullScreen
        />
      ) : (
        <button type="button" onClick={() => setPlaying(true)}>
          <Image src={poster} width={1600} height={900} alt="" sizes="(max-width: 760px) 92vw, 80vw" />
          <span className="lf-trailer-play">
            Play the trailer <span className="lf-trailer-time">0:31</span>
          </span>
        </button>
      )}
    </div>
  );
}
