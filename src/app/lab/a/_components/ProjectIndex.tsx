"use client";

import Image from "next/image";
import { useState } from "react";
import { projects } from "@/lab/content";

const pad = (n: number) => String(n).padStart(2, "0");
const host = (href: string) => new URL(href).host.replace(/^www\./, "");

export default function ProjectIndex() {
  const [active, setActive] = useState(0);
  const current = projects[active];

  return (
    <div className="grid md:grid-cols-12">
      <ol className="md:col-span-7 md:border-r border-(--line)">
        {projects.map((p, i) => (
          <li key={p.slug} className="border-b border-(--line) last:border-b-0">
            <a
              href={p.href}
              target="_blank"
              rel="noreferrer"
              data-active={active === i}
              onMouseEnter={() => setActive(i)}
              onFocus={() => setActive(i)}
              className="row group relative grid grid-cols-[2.75rem_1fr] gap-x-3 px-4 py-6 md:grid-cols-[4.5rem_1fr] md:px-6 md:py-8 hover:bg-(--bg-2) transition-colors"
            >
              <span aria-hidden className="row-bar absolute inset-y-0 left-0 w-0.5 bg-(--signal)" />
              <span className="row-index mono-lc pt-2 text-(--ink-3)">{pad(i + 1)}</span>

              <div className="min-w-0">
                <div className="flex items-start justify-between gap-4">
                  <h3 className="text-[28px] font-medium leading-none tracking-[-0.03em] md:text-[40px]">
                    {p.title}
                  </h3>
                  <span className="row-arrow mt-1 text-xl leading-none text-(--ink-3)" aria-hidden>
                    ↗
                  </span>
                </div>

                <p className="mono mt-3 flex items-center gap-2 text-(--ink-3)">
                  <span
                    aria-hidden
                    className={`inline-block h-2 w-2 ${
                      p.kind === "case-study" ? "bg-(--signal)" : "border border-(--ink-3)"
                    }`}
                  />
                  {p.kind === "case-study" ? "Case study" : "Entry"}
                  <span className="text-(--line-2)">/</span>
                  <span className="normal-case">{host(p.href)}</span>
                </p>

                <div className="relative mt-5 aspect-[16/10] overflow-hidden border border-(--line) md:hidden">
                  <Image
                    src={p.image}
                    alt={`${p.title} preview`}
                    fill
                    sizes="100vw"
                    quality={70}
                    className="object-cover object-top"
                  />
                </div>

                <p className="mt-4 max-w-[52ch] text-[15px] leading-relaxed text-(--ink-2)">
                  {p.summary}
                </p>
                <p className="mono-lc mt-4 text-(--ink-3)">{p.tags.join("  ·  ")}</p>
              </div>
            </a>
          </li>
        ))}
      </ol>

      <aside aria-hidden className="hidden md:col-span-5 md:block">
        <div className="sticky top-(--header-h) p-6">
          <div className="mono mb-4 flex justify-between text-(--ink-3)">
            <span>Fig. {pad(active + 1)}</span>
            <span>Preview</span>
          </div>
          <div className="relative aspect-[16/10] border border-(--line) bg-(--bg-2)">
            <span className="crop crop--tl" />
            <span className="crop crop--tr" />
            <span className="crop crop--bl" />
            <span className="crop crop--br" />
            <div className="absolute inset-0 overflow-hidden">
              {projects.map((p, i) => (
                <Image
                  key={p.slug}
                  src={p.image}
                  alt=""
                  fill
                  sizes="(min-width: 1440px) 560px, 40vw"
                  quality={70}
                  data-active={active === i}
                  className="preview-img object-cover object-top"
                />
              ))}
            </div>
          </div>
          <dl className="mono mt-4 grid grid-cols-[6rem_1fr] gap-y-1.5 text-(--ink-3)">
            <dt>Title</dt>
            <dd className="text-(--ink)">{current.title}</dd>
            <dt>Type</dt>
            <dd className="text-(--ink-2)">{current.kind === "case-study" ? "Case study" : "Entry"}</dd>
            <dt>Stack</dt>
            <dd className="text-(--ink-2)">{current.tags.length} items</dd>
            <dt>Source</dt>
            <dd className="normal-case text-(--ink-2)">{host(current.href)}</dd>
          </dl>
        </div>
      </aside>
    </div>
  );
}
