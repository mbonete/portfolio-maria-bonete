"use client";

import { useState } from "react";
import Hero from "./Hero";

type Ground = "blue" | "red";

export default function Shell({ initialGround, children }: { initialGround: Ground; children: React.ReactNode }) {
  const [ground, setGround] = useState<Ground>(initialGround);

  const choose = (g: Ground) => {
    setGround(g);
    const url = new URL(window.location.href);
    if (g === "red") url.searchParams.set("ground", "red");
    else url.searchParams.delete("ground");
    window.history.replaceState(null, "", url);
  };

  return (
    <div className="ld" data-ground={ground}>
      <Hero ground={ground} onGround={choose} />
      {children}
    </div>
  );
}
