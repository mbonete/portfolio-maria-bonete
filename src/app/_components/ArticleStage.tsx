"use client";

import { useEffect, useState } from "react";

// The phone beside an article (wide screens): it shows the screen of the section being read. A section
// counts as being read once its heading passes 40% of the window's height; a section without a screen
// keeps the one before it. Above the first heading, the first section counts. The rule numbers under
// the caption, and the contents list at the top of the text, mark the same section in gold.
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
    const update = () => {
      const line = window.innerHeight * 0.4;
      let at = 0;
      headings.forEach((h, i) => {
        if (h.getBoundingClientRect().top < line) at = i;
      });
      setCurrent(at);
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, [sections]);

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
