"use client";

import { useState, useSyncExternalStore } from "react";

type Technique = { title: string; body: string; tags: string[] };

const noopSubscribe = () => () => {};

// Every technique renders without a script. Once hydrated, phones fold the list to its first three,
// so the AI section stays readable; wider screens ignore the fold in CSS.
export default function Toolkit({ items }: { items: Technique[] }) {
  const [open, setOpen] = useState(false);
  const hydrated = useSyncExternalStore(noopSubscribe, () => true, () => false);

  return (
    <>
      <ul id="le-toolkit" className="le-toolkit" data-folded={(hydrated && !open) || undefined}>
        {items.map((t) => (
          <li key={t.title}>
            <h4>{t.title}</h4>
            <p>{t.body}</p>
            <p className="le-tags">
              {t.tags.map((g) => (
                <code key={g}>{g}</code>
              ))}
            </p>
          </li>
        ))}
      </ul>
      {hydrated && (
        <button
          type="button"
          className="le-toolkit-more"
          aria-expanded={open}
          aria-controls="le-toolkit"
          onClick={() => setOpen(!open)}
        >
          {open ? "Show fewer" : `Show all ${items.length} techniques`}
        </button>
      )}
    </>
  );
}
