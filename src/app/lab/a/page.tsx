import Image from "next/image";
import Clock from "./_components/Clock";
import CommandPalette from "./_components/CommandPalette";
import ProjectIndex from "./_components/ProjectIndex";
import { currently, person, projects } from "@/lab/content";

const caseStudies = projects.filter((p) => p.kind === "case-study").length;
const pad = (n: number) => String(n).padStart(2, "0");
const [first, last] = person.name.split(" ");

function SectionHead({ index, title, meta, id }: { index: number; title: string; meta: React.ReactNode; id?: string }) {
  return (
    <div id={id} className="relative grid scroll-mt-(--header-h) grid-cols-[2.75rem_1fr_auto] items-center border-b border-(--line) md:grid-cols-[4.5rem_1fr_auto]">
      <span className="mono border-r border-(--line) px-4 py-3 text-(--signal) md:px-6">{pad(index)}</span>
      <h2 className="px-4 py-3 text-sm font-medium md:px-6">{title}</h2>
      <span className="mono px-4 text-(--ink-3) md:px-6">{meta}</span>
    </div>
  );
}

function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-(--line) bg-(--bg)">
      <div className="mx-auto flex h-(--header-h) max-w-[1440px] items-stretch border-x border-(--line)">
        <a href="#" className="mono flex items-center gap-3 border-r border-(--line) px-4 md:px-6">
          <span aria-hidden className="inline-block h-2.5 w-2.5 bg-(--signal)" />
          <span className="text-(--ink)">M. Bonete</span>
        </a>
        <div className="mono hidden flex-1 items-center gap-6 px-6 text-(--ink-3) lg:flex">
          <span>ES / {person.timezone}</span>
          <Clock className="text-(--ink-2) tabular-nums" />
        </div>
        <nav aria-label="Primary" className="ml-auto flex items-stretch">
          <ul className="mono hidden items-stretch md:flex">
            {[
              ["01", "Work", "#projects"],
              ["02", "Contact", "#contact"],
            ].map(([n, label, href]) => (
              <li key={href} className="flex">
                <a href={href} className="flex items-center gap-2 border-l border-(--line) px-5 text-(--ink-2) hover:bg-(--bg-2) hover:text-(--ink) transition-colors">
                  <span className="text-(--ink-3)">{n}</span>
                  {label}
                </a>
              </li>
            ))}
          </ul>
          <CommandPalette />
        </nav>
      </div>
    </header>
  );
}

function Hero() {
  const [lead, ...rest] = person.specialties;
  return (
    <section aria-labelledby="hero-name" className="relative border-b border-(--line)">
      <div className="mono grid grid-cols-2 border-b border-(--line) text-(--ink-3) md:grid-cols-12">
        <span className="border-r border-(--line) px-4 py-3 md:col-span-2 md:px-6">00 / Index</span>
        <span className="px-4 py-3 md:col-span-4 md:border-r md:border-(--line) md:px-6">Portfolio — rev. 2026.10</span>
        <span className="hidden px-6 py-3 md:col-span-3 md:block md:border-r md:border-(--line)">{person.role}</span>
        <span className="hidden px-6 py-3 md:col-span-3 md:block">Based in {person.location}</span>
      </div>

      <div className="grid md:grid-cols-12">
        <div className="relative px-4 pb-10 pt-10 md:col-span-8 md:border-r md:border-(--line) md:px-6 md:pb-14 md:pt-16">
          <h1 id="hero-name" className="display text-[clamp(76px,13.2vw,184px)]">
            <span className="block">{first}</span>
            <span className="block">
              {last}
              <span aria-hidden className="blink ml-[0.04em] inline-block h-[0.07em] w-[0.42em] bg-(--signal) align-baseline" />
            </span>
          </h1>

          <div className="mt-10 grid gap-8 md:mt-14 md:grid-cols-8">
            <p className="text-[21px] leading-[1.35] tracking-[-0.01em] text-(--ink-2) md:col-span-5 md:text-[24px]">
              <span className="text-(--ink)">{person.role}</span>, specialising in{" "}
              <span className="text-(--ink)">{lead}</span>,{" "}
              <span className="text-(--ink)">{rest[0]}</span> and{" "}
              <span className="text-(--ink)">{rest[1]}</span>.
            </p>
            <div className="mono hidden self-end text-(--ink-3) md:col-span-3 md:block">
              <p>Focus</p>
              <ol className="mt-2 space-y-1 text-(--ink-2)">
                {person.specialties.map((s, i) => (
                  <li key={s}>
                    <span className="text-(--ink-3)">{pad(i + 1)}</span>&nbsp;&nbsp;{s}
                  </li>
                ))}
              </ol>
            </div>
          </div>

          <div className="mt-10 flex flex-wrap items-stretch gap-3">
            <a href="#projects" className="btn-signal flex h-12 items-center gap-8 bg-(--signal) px-5 text-[15px] font-medium text-(--bg)">
              Selected work <span aria-hidden>↘</span>
            </a>
            <a href={person.links.cv} target="_blank" rel="noreferrer" className="btn-line flex h-12 items-center gap-8 border border-(--line-2) px-5 text-[15px]">
              Curriculum <span className="mono text-(--ink-3)">PDF ↗</span>
            </a>
          </div>
          <p className="mono mt-6 flex gap-6 text-(--ink-2)">
            <a className="ulink" href={person.links.github} target="_blank" rel="noreferrer">GitHub ↗</a>
            <a className="ulink" href={person.links.linkedin} target="_blank" rel="noreferrer">LinkedIn ↗</a>
          </p>
        </div>

        <figure className="relative border-t border-(--line) px-4 py-10 md:col-span-4 md:border-t-0 md:px-6 md:py-16">
          <div className="mono mb-4 flex justify-between text-(--ink-3)">
            <span>Fig. 00</span>
            <span>430 × 448</span>
          </div>
          <div className="flex gap-3">
            <div aria-hidden className="ruler w-3 shrink-0" />
            <div className="relative flex-1 border border-(--line) bg-(--bg-2)">
              <span className="crop crop--tl" />
              <span className="crop crop--tr" />
              <span className="crop crop--bl" />
              <span className="crop crop--br" />
              <div className="relative mx-auto aspect-[430/448] max-w-[340px] md:max-w-none">
                <Image
                  src={person.cutout}
                  alt={`Portrait of ${person.name}`}
                  fill
                  priority
                  sizes="(min-width: 768px) 30vw, 80vw"
                  className="photo object-contain object-bottom"
                />
              </div>
              {/* Registration crosshair, kept off the subject */}
              <span aria-hidden className="absolute left-5 top-5 h-5 w-5">
                <span className="absolute left-1/2 top-0 h-full w-px bg-(--signal)" />
                <span className="absolute left-0 top-1/2 h-px w-full bg-(--signal)" />
              </span>
            </div>
          </div>
          <figcaption className="mono mt-4 grid grid-cols-[5rem_1fr] gap-y-1 text-(--ink-3)">
            <span>Subject</span>
            <span className="text-(--ink-2)">{person.name}</span>
            <span>Based</span>
            <span className="text-(--ink-2)">{person.location}</span>
            <span>Local</span>
            <Clock className="tabular-nums text-(--ink-2)" />
          </figcaption>
        </figure>
      </div>

      <dl className="grid grid-cols-1 border-t border-(--line) sm:grid-cols-2 md:grid-cols-12">
        {[
          ["Now", currently.role, "md:col-span-4"],
          ["Building", currently.building, "md:col-span-4"],
          ["Stack", "TypeScript · React · Next.js · Expo · Node", "md:col-span-4"],
        ].map(([k, v, span], i) => (
          <div
            key={k}
            className={`${span} border-(--line) px-4 py-5 md:px-6 ${i > 0 ? "border-t sm:border-t-0 sm:border-l" : ""} ${i === 2 ? "sm:col-span-2 sm:border-l-0 sm:border-t md:border-t-0 md:border-l" : ""}`}
          >
            <dt className="mono text-(--ink-3)">{k}</dt>
            <dd className="mt-2 text-[15px] text-(--ink)">{v}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function Contact() {
  const links = [
    ["GitHub", "github.com/mbonete", person.links.github],
    ["LinkedIn", "in/maria-bonete", person.links.linkedin],
    ["Curriculum", "cv.pdf", person.links.cv],
  ];
  return (
    <section aria-label="Contact">
      <SectionHead id="contact" index={2} title="Contact" meta={`${pad(links.length)} channels`} />
      <ul className="grid md:grid-cols-3">
        {links.map(([label, value, href], i) => (
          <li key={label} className={`border-b border-(--line) md:border-b-0 ${i > 0 ? "md:border-l" : ""}`}>
            <a href={href} target="_blank" rel="noreferrer" className="row group flex items-end justify-between gap-4 px-4 py-8 hover:bg-(--bg-2) transition-colors md:px-6 md:py-12">
              <span>
                <span className="mono block text-(--ink-3)">{label}</span>
                <span className="mt-2 block text-[22px] tracking-[-0.02em] md:text-[26px]">{value}</span>
              </span>
              <span aria-hidden className="row-arrow text-xl text-(--ink-3)">↗</span>
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function InstrumentPage() {
  return (
    <>
      <Header />
      <main className="mx-auto max-w-[1440px] border-x border-(--line)">
        <Hero />
        <section aria-label="Selected work" className="border-b border-(--line)">
          <SectionHead
            id="projects"
            index={1}
            title="Selected work"
            meta={
              <>
                {pad(projects.length)} entries
                <span className="hidden sm:inline"> · {pad(caseStudies)} case studies</span>
              </>
            }
          />
          <ProjectIndex />
        </section>
        <Contact />
      </main>
      <footer className="mx-auto max-w-[1440px] border-x border-t border-(--line)">
        <div className="mono flex flex-wrap justify-between gap-4 px-4 py-4 text-(--ink-3) md:px-6">
          <span>© {new Date().getFullYear()} {person.name}</span>
          <span>POC A — Instrument</span>
        </div>
      </footer>
    </>
  );
}
