"use client";

import Image from "next/image";
import { useState, type MouseEvent } from "react";
import { Play } from "lucide-react";

type Props = {
  videoId: string;
  title: string;
  poster: string;
};

export default function LiteYouTube({ videoId, title, poster }: Props) {
  const [active, setActive] = useState(false);

  const activate = (e: MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setActive(true);
  };

  return (
    <div className="relative aspect-video overflow-hidden rounded-xl my-4 bg-neutral-900">
      {active ? (
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="absolute inset-0 h-full w-full"
        />
      ) : (
        <button
          type="button"
          onClick={activate}
          aria-label={`Play video: ${title}`}
          className="group/video absolute inset-0 cursor-pointer"
        >
          <Image
            src={poster}
            alt=""
            fill
            sizes="(min-width: 1024px) 580px, (min-width: 640px) 50vw, 100vw"
            className="object-cover"
          />
          <span className="absolute inset-0 flex items-center justify-center bg-black/30 group-hover/video:bg-black/20 transition-colors">
            <span className="flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-[0_0_40px_-5px_var(--color-primary)] group-hover/video:scale-110 transition-transform">
              <Play className="h-6 w-6 translate-x-0.5" fill="currentColor" />
            </span>
          </span>
        </button>
      )}
    </div>
  );
}
