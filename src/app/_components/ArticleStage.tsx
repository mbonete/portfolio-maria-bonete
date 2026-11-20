"use client";

import { useEffect, useState } from "react";

// The phone beside an article (wide screens): it shows the screen of the section being read. A section
// counts as being read once its heading passes 40% of the window's height; a section without a screen
// keeps the one before it, and above the first heading the first section counts. The rule numbers under
// the caption, and the contents list at the top of the text, mark the same section.
//
// The phone changes only once scrolling has settled for a moment, so a fast scroll past several rules
// doesn't flash every screen on the way. Links to a section scroll to it and update the address in
// place, without adding a history entry, so the browser's Back button leaves the article for the page
// before it rather than stepping back through sections.
const SETTLE_MS = 140;

export default function ArticleStage({
  sections,
  captions,
  rules,
  children,
}: {
  sections: { id: string; screen: number }[];
  captions: string[];
  rules: { id: string; number: string; title: string }[];
  children: React.ReactNode[]; // one image per screen, in order
}) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const headings = sections
      .map((s) => document.getElementById(s.id))
      .filter((h): h is HTMLElement => h !== null);
    const reading = () => {
      const line = window.innerHeight * 0.4;
      let at = 0;
      headings.forEach((h, i) => {
        if (h.getBoundingClientRect().top < line) at = i;
      });
      return at;
    };
    let timer: ReturnType<typeof setTimeout> | undefined;
    const settle = () => {
      clearTimeout(timer);
      timer = setTimeout(() => setCurrent(reading()), SETTLE_MS);
    };
    // The first reading, once laid out: a page opened at a section starts on that section's screen.
    const first = requestAnimationFrame(() => setCurrent(reading()));
    window.addEventListener("scroll", settle, { passive: true });
    window.addEventListener("resize", settle);
    return () => {
      cancelAnimationFrame(first);
      clearTimeout(timer);
      window.removeEventListener("scroll", settle);
      window.removeEventListener("resize", settle);
    };
  }, [sections]);

  // Section links (the contents and the rule numbers) move within the page without adding history.
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      const link = (e.target as Element).closest<HTMLAnchorElement>(".lf-p-toc a, .lf-p-rules a");
      const target = link && document.getElementById(link.hash.slice(1));
      if (!link || !target) return;
      e.preventDefault();
      const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      target.scrollIntoView({ behavior: still ? "auto" : "smooth", block: "start" });
      history.replaceState(history.state, "", link.hash);
    };
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  useEffect(() => {
    const id = sections[current]?.id;
    document.querySelectorAll<HTMLAnchorElement>(".lf-p-toc a").forEach((a) => {
      if (a.hash === `#${id}`) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  }, [current, sections]);

  const shown = sections[current]?.screen ?? 0;
  return (
    <div className="lf-p-stage-in">
      <div className="lf-phone">
        <div className="lf-phone-screen lf-p-screens">
          {children.map((image, i) => (
            <div key={i} className="lf-p-screen" data-on={i === shown || undefined} aria-hidden={i !== shown}>
              {image}
            </div>
          ))}
        </div>
      </div>
      <p className="lf-p-caption" aria-live="polite">
        {captions[shown]}
      </p>
      <ol className="lf-p-rules" aria-label="Rules">
        {rules.map((r) => (
          <li key={r.id}>
            <a href={`#${r.id}`} title={r.title} aria-current={r.id === sections[current]?.id || undefined}>
              {r.number}
            </a>
          </li>
        ))}
      </ol>
    </div>
  );
}
