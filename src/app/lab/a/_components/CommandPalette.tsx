"use client";

import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";
import { person, projects, sections } from "@/lab/content";

type Item = {
  id: string;
  group: "Navigate" | "Projects" | "Links" | "Actions";
  label: string;
  hint: string;
  keywords?: string;
  run: () => void | Promise<void>;
};

const GROUPS: Item["group"][] = ["Navigate", "Projects", "Links", "Actions"];

// Subsequence match: rewards consecutive characters and word starts.
function score(query: string, text: string) {
  const q = query.trim().toLowerCase();
  if (!q) return 1;
  const t = text.toLowerCase();
  let from = 0;
  let streak = 0;
  let total = 0;
  for (const ch of q) {
    if (ch === " ") continue;
    const i = t.indexOf(ch, from);
    if (i < 0) return 0;
    streak = i === from ? streak + 1 : 0;
    const wordStart = i === 0 || t[i - 1] === " " || t[i - 1] === "-";
    total += 1 + streak * 2 + (wordStart ? 3 : 0);
    from = i + 1;
  }
  return total - t.length * 0.01;
}

const prefersReducedMotion = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function scrollToId(id: string) {
  const el = id === "top" ? document.body : document.getElementById(id);
  if (!el) return;
  const behavior = prefersReducedMotion() ? "auto" : "smooth";
  if (id === "top") window.scrollTo({ top: 0, behavior });
  else el.scrollIntoView({ behavior, block: "start" });
  history.replaceState(null, "", id === "top" ? location.pathname : `#${id}`);
}

const openExternal = (href: string) => {
  window.open(href, "_blank", "noopener,noreferrer");
};

const isMac = () => /Mac|iPhone|iPad/.test(navigator.platform);
const noopSubscribe = () => () => {};

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const [status, setStatus] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const restoreRef = useRef<HTMLElement | null>(null);
  const listId = useId();
  const mac = useSyncExternalStore(noopSubscribe, isMac, () => true);

  const show = useCallback(() => {
    restoreRef.current = document.activeElement as HTMLElement | null;
    setQuery("");
    setActive(0);
    setStatus(null);
    setOpen(true);
  }, []);

  const hide = useCallback(() => {
    setOpen(false);
    const el = restoreRef.current;
    requestAnimationFrame(() => el?.focus?.());
  }, []);

  // Global shortcut, plus ?palette=1 to open on load (for screenshots/demos).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (open) hide();
        else show();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, show, hide]);

  useEffect(() => {
    if (!new URLSearchParams(location.search).has("palette")) return;
    const id = requestAnimationFrame(show);
    return () => cancelAnimationFrame(id);
  }, [show]);

  useEffect(() => {
    if (!open) return;
    const root = document.documentElement;
    const prev = root.style.overflow;
    root.style.overflow = "hidden";
    inputRef.current?.focus();
    return () => {
      root.style.overflow = prev;
    };
  }, [open]);

  const items = useMemo<Item[]>(() => {
    if (!open) return [];
    const nav: Item[] = [
      { id: "top", label: "Top" },
      ...sections.map((s) => ({ id: s.id, label: s.label })),
    ]
      .filter((s) => s.id === "top" || document.getElementById(s.id))
      .map((s, i) => ({
        id: `nav-${s.id}`,
        group: "Navigate" as const,
        label: `Go to ${s.label}`,
        hint: String(i).padStart(2, "0"),
        keywords: "section jump scroll",
        run: () => scrollToId(s.id),
      }));

    const work: Item[] = projects.map((p) => ({
      id: `project-${p.slug}`,
      group: "Projects",
      label: p.title,
      hint: p.kind === "case-study" ? "Case study" : "Entry",
      keywords: p.tags.join(" "),
      run: () => openExternal(p.href),
    }));

    const links: Item[] = [
      { id: "cv", label: "Open CV", hint: "PDF", keywords: "resume curriculum", href: person.links.cv },
      { id: "github", label: "GitHub", hint: "mbonete", keywords: "code repos", href: person.links.github },
      { id: "linkedin", label: "LinkedIn", hint: "maria-bonete", keywords: "profile", href: person.links.linkedin },
    ].map(({ href, ...l }) => ({ ...l, group: "Links" as const, run: () => openExternal(href) }));

    const actions: Item[] = [
      {
        id: "copy-url",
        group: "Actions",
        label: "Copy page URL",
        hint: "Share",
        keywords: "link clipboard",
        run: async () => {
          try {
            await navigator.clipboard.writeText(location.origin + location.pathname);
            setStatus("Copied to clipboard");
          } catch {
            setStatus("Clipboard unavailable");
          }
        },
      },
    ];

    return [...nav, ...work, ...links, ...actions];
  }, [open]);

  const results = useMemo(() => {
    const scored = items
      .map((item) => ({
        item,
        s: Math.max(
          score(query, item.label) * 1.5,
          score(query, `${item.group} ${item.keywords ?? ""} ${item.hint}`),
        ),
      }))
      .filter((r) => r.s > 0);
    if (query.trim()) scored.sort((a, b) => b.s - a.s);
    else scored.sort((a, b) => GROUPS.indexOf(a.item.group) - GROUPS.indexOf(b.item.group));
    return scored.map((r) => r.item);
  }, [items, query]);

  const current = Math.min(active, Math.max(results.length - 1, 0));

  useEffect(() => {
    listRef.current
      ?.querySelector(`[data-index="${current}"]`)
      ?.scrollIntoView({ block: "nearest" });
  }, [current]);

  const runItem = (item: Item | undefined) => {
    if (!item) return;
    if (item.group === "Actions") {
      void item.run();
      return;
    }
    setOpen(false);
    // Let the dialog unmount and scroll lock release before navigating.
    requestAnimationFrame(() => void item.run());
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActive((current + 1) % Math.max(results.length, 1));
        break;
      case "ArrowUp":
        e.preventDefault();
        setActive((current - 1 + results.length) % Math.max(results.length, 1));
        break;
      case "Home":
        e.preventDefault();
        setActive(0);
        break;
      case "End":
        e.preventDefault();
        setActive(results.length - 1);
        break;
      case "Enter":
        e.preventDefault();
        runItem(results[current]);
        break;
      case "Escape":
        e.preventDefault();
        hide();
        break;
      case "Tab":
        // Focus is trapped on the input; options are reached via aria-activedescendant.
        e.preventDefault();
        break;
    }
  };

  const optionId = (i: number) => `${listId}-opt-${i}`;
  let lastGroup: string | null = null;

  return (
    <>
      <button
        type="button"
        onClick={show}
        aria-haspopup="dialog"
        aria-keyshortcuts="Meta+K Control+K"
        className="mono flex h-full items-center gap-3 border-l border-(--line) px-4 text-(--ink-2) hover:bg-(--bg-2) hover:text-(--ink) transition-colors"
      >
        <span className="hidden sm:inline">Command</span>
        <kbd className="border border-(--line-2) px-1.5 py-0.5 text-(--ink) normal-case">
          {mac ? "⌘K" : "Ctrl K"}
        </kbd>
      </button>

      {open && (
        <div className="fixed inset-0 z-50">
          <div
            aria-hidden
            className="pal-scrim absolute inset-0 bg-[#0b0a09]/80"
            onMouseDown={hide}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Command palette"
            className="pal-enter absolute left-1/2 top-[12vh] w-[min(640px,calc(100vw-2rem))] -translate-x-1/2 border border-(--line-2) bg-(--bg-2) shadow-[0_24px_80px_-20px_rgba(0,0,0,0.8)]"
            onKeyDown={onKeyDown}
          >
            <span aria-hidden className="crop crop--tl" />
            <span aria-hidden className="crop crop--tr" />
            <span aria-hidden className="crop crop--bl" />
            <span aria-hidden className="crop crop--br" />

            <div className="flex items-center gap-3 border-b border-(--line) px-4">
              <span aria-hidden className="mono-lc text-(--signal)">
                &gt;
              </span>
              <input
                ref={inputRef}
                role="combobox"
                aria-expanded="true"
                aria-controls={listId}
                aria-activedescendant={results.length ? optionId(current) : undefined}
                aria-autocomplete="list"
                aria-label="Type a command or search"
                placeholder="Type a command or search…"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setActive(0);
                  setStatus(null);
                }}
                className="pal-input h-14 flex-1 bg-transparent text-[17px] text-(--ink) placeholder:text-(--ink-3) outline-none"
                autoComplete="off"
                spellCheck={false}
              />
              <button
                type="button"
                onClick={hide}
                className="mono border border-(--line-2) px-1.5 py-0.5 text-(--ink-2) hover:text-(--ink)"
              >
                Esc
              </button>
            </div>

            <ul
              ref={listRef}
              id={listId}
              role="listbox"
              aria-label="Commands"
              className="max-h-[min(420px,55vh)] overflow-y-auto py-2"
            >
              {results.length === 0 && (
                <li role="presentation" className="mono px-4 py-6 text-(--ink-3)">
                  No match for “{query}”
                </li>
              )}
              {results.map((item, i) => {
                const heading = item.group !== lastGroup && !query.trim();
                lastGroup = item.group;
                const selected = i === current;
                return (
                  <li key={item.id} role="presentation">
                    {heading && (
                      <div
                        role="presentation"
                        className="mono px-4 pb-1 pt-3 text-(--ink-3)"
                      >
                        {item.group}
                      </div>
                    )}
                    <div
                      id={optionId(i)}
                      role="option"
                      aria-selected={selected}
                      data-index={i}
                      onMouseMove={() => current !== i && setActive(i)}
                      onClick={() => runItem(item)}
                      className={`relative flex cursor-pointer items-center justify-between gap-4 px-4 py-2.5 ${
                        selected ? "bg-(--bg-3) text-(--ink)" : "text-(--ink-2)"
                      }`}
                    >
                      <span
                        aria-hidden
                        className={`absolute inset-y-0 left-0 w-0.5 ${selected ? "bg-(--signal)" : ""}`}
                      />
                      <span className="truncate text-[15px]">{item.label}</span>
                      <span className="mono shrink-0 text-(--ink-3)">
                        {selected ? "↵" : item.hint}
                      </span>
                    </div>
                  </li>
                );
              })}
            </ul>

            <div className="mono flex items-center justify-between gap-4 border-t border-(--line) px-4 py-2.5 text-(--ink-3)">
              <span className="hidden sm:inline">↑↓ Navigate · ↵ Open · Esc Close</span>
              <span role="status" aria-live="polite" className={status ? "text-(--signal)" : ""}>
                {status ?? `${String(results.length).padStart(2, "0")} results`}
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
