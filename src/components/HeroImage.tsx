"use client";

import Image from "next/image";
import { useState } from "react";

export default function HeroImage() {
  const [loaded, setLoaded] = useState(false);

  return (
    <>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/neonimage-lqip.webp"
        alt=""
        aria-hidden
        className={`absolute inset-0 w-full h-full object-contain select-none pointer-events-none blur-md scale-110 transition-opacity duration-500 ${
          loaded ? "opacity-0" : "opacity-95"
        }`}
      />
      <Image
        ref={(node) => {
          if (node?.complete) setLoaded(true);
        }}
        src="/neonimage.webp"
        alt=""
        aria-hidden
        fill
        sizes="(min-width: 768px) 420px, 176px"
        quality={65}
        priority
        onLoad={() => setLoaded(true)}
        className={`object-contain select-none pointer-events-none transition-opacity duration-500 ${
          loaded ? "opacity-95" : "opacity-0"
        }`}
      />
    </>
  );
}
