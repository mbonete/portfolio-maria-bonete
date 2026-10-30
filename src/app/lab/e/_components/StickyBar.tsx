"use client";

import { useEffect, useState } from "react";
import { person } from "@/lab/content";
import Seal from "./Seal";

const links = [
  { id: "projects", label: "Work" },
  { id: "ai", label: "AI" },
  { id: "experience", label: "Experience" },
];
const tracked = [...links.map((l) => l.id), "about", "contact"];

// The hero's nav scrolls away with the hero; this strip of lacquer takes over from there, so the CV
// and a way to reach her stay one tap away and the visitor can see where they are.
export default function StickyBar() {
  const [shown, setShown] = useState(false);
  const [current, setCurrent] = useState<string | null>(null);

  useEffect(() => {
    const hero = document.querySelector(".le-hero");
    if (!hero) return;
    const heroWatch = new IntersectionObserver(([e]) => setShown(!e.isIntersecting), {
      rootMargin: "-64px 0px 0px 0px",
    });
    heroWatch.observe(hero);

    // A line across the middle of the screen: whichever section crosses it is the current one.
    const spy = new IntersectionObserver(
      (entries) => {
        for (const e of entries) if (e.isIntersecting) setCurrent(e.target.id);
      },
      { rootMargin: "-50% 0px -50% 0px" },
    );
    for (const id of tracked) {
      const el = document.getElementById(id);
      if (el) spy.observe(el);
    }
    return () => {
      heroWatch.disconnect();
      spy.disconnect();
    };
  }, []);

  return (
    <nav className="le-bar" data-shown={shown || undefined} aria-label="Sections">
      <Seal label="Maria Bonete, back to the top" />
      {links.map((l) => (
        <a key={l.id} href={`#${l.id}`} aria-current={current === l.id ? "true" : undefined}>
          {l.label}
        </a>
      ))}
      <span className="le-bar-end">
        <a href={person.links.cv} target="_blank" rel="noreferrer">
          CV
        </a>
        <a href="#contact" aria-current={current === "contact" ? "true" : undefined}>
          Contact
        </a>
      </span>
    </nav>
  );
}
