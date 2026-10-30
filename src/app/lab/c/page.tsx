import Image from "next/image";
import { Fragment_Mono, Hanken_Grotesk } from "next/font/google";
import { currently, person, projects, type Project } from "@/lab/content";
import DitherPortrait from "./_components/DitherPortrait";
import MadridClock from "./_components/MadridClock";

const sans = Hanken_Grotesk({ subsets: ["latin"], variable: "--c-sans" });
const mono = Fragment_Mono({ subsets: ["latin"], weight: "400", variable: "--c-mono" });

const INK = "#c8f031";

const tokens = {
  "--c-bg": "#0e0e0c",
  "--c-fg": "#ece9e1",
  "--c-muted": "#8b887f",
  "--c-line": "#2a2925",
  "--c-ink": INK,
} as React.CSSProperties;

const monoCls = "font-(family-name:--c-mono) text-[12px] leading-5 tracking-[0.01em]";
const grid = "grid grid-cols-4 gap-x-4 md:grid-cols-12 md:gap-x-6";

function linkLabel(href: string) {
  return href.includes("github.com") ? "Source" : "Live site";
}

function ProjectMeta({ project, index, large }: { project: Project; index: number; large?: boolean }) {
  return (
    <div className="flex flex-col">
      <div className={`${monoCls} flex justify-between text-(--c-muted)`}>
        <span>({String(index + 1).padStart(2, "0")})</span>
        <span>{project.kind === "case-study" ? "Case study" : "Project"}</span>
      </div>
      <h3
        className={`mt-3 font-medium tracking-[-0.03em] underline decoration-transparent decoration-1 underline-offset-[0.18em] transition-colors group-hover:decoration-(--c-ink) ${
          large ? "text-[34px] leading-none md:text-[44px]" : "text-[26px] leading-none"
        }`}
      >
        {project.title}
      </h3>
      <p className="mt-4 max-w-[38ch] text-[15px] leading-[1.55] text-(--c-fg)/80">{project.summary}</p>
      <p className={`${monoCls} mt-5 text-(--c-muted)`}>{project.tags.join(" / ")}</p>
      <span className={`${monoCls} mt-5 text-(--c-fg) group-hover:text-(--c-ink)`}>
        {linkLabel(project.href)} ↗
      </span>
    </div>
  );
}

function ProjectImage({ project, sizes, aspect }: { project: Project; sizes: string; aspect: string }) {
  return (
    <div
      className={`relative ${aspect} overflow-hidden bg-[#1a1a17] outline-1 outline-offset-4 outline-transparent transition-[outline-color] group-hover:outline-(--c-ink)`}
    >
      <Image
        src={project.image}
        alt={`${project.title} preview`}
        fill
        sizes={sizes}
        quality={70}
        className="object-cover grayscale-[35%] transition duration-500 group-hover:grayscale-0"
      />
    </div>
  );
}

export default function PocC() {
  const [featureA, featureB, ...entries] = projects;

  return (
    <div
      style={tokens}
      className={`${sans.variable} ${mono.variable} flex-1 bg-(--c-bg) font-(family-name:--c-sans) text-(--c-fg) antialiased selection:bg-(--c-ink) selection:text-(--c-bg)`}
    >
      <div className="mx-auto w-full max-w-400 px-4 md:px-10">
        {/* Masthead */}
        <header className={`${grid} ${monoCls} items-baseline border-b border-(--c-line) py-4`}>
          <a href="#top" className="col-span-2 md:col-span-3 hover:text-(--c-ink)">
            Maria Bonete
          </a>
          <nav aria-label="Sections" className="hidden gap-6 text-(--c-muted) md:col-span-6 md:flex">
            <a href="#projects" className="hover:text-(--c-fg)">Work</a>
            <a href="#ai" className="hover:text-(--c-fg)">AI</a>
            <a href="#experience" className="hover:text-(--c-fg)">Experience</a>
            <a href="#contact" className="hover:text-(--c-fg)">Contact</a>
          </nav>
          <p className="col-span-2 text-right text-(--c-muted) md:col-span-3">
            Madrid <span className="text-(--c-fg)"><MadridClock /></span>
          </p>
        </header>

        {/* Hero */}
        <section id="top" className={`${grid} gap-y-12 pt-10 pb-14 md:pt-16 md:pb-20`}>
          <div className="col-span-4 flex flex-col md:col-span-7">
            <h1 className="text-[clamp(68px,11.5vw,188px)] leading-[0.84] font-medium tracking-[-0.06em]">
              Maria
              <br />
              Bonete
            </h1>
            <p className="mt-8 max-w-[22ch] text-[24px] leading-[1.18] tracking-[-0.02em] md:mt-12 md:text-[30px]">
              {person.role}, specialising in {person.specialties[0]}, {person.specialties[1]} and{" "}
              <span className="underline decoration-(--c-ink) decoration-2 underline-offset-[0.2em]">
                {person.specialties[2]}
              </span>
              .
            </p>
            <div className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-5">
              <a
                href="#projects"
                className="inline-flex h-12 items-center gap-6 bg-(--c-ink) px-5 text-[15px] font-medium text-(--c-bg) transition-colors hover:bg-(--c-fg)"
              >
                Selected work <span aria-hidden>↓</span>
              </a>
              <a
                href={person.links.cv}
                className="border-b border-(--c-fg)/40 pb-0.5 text-[15px] transition-colors hover:border-(--c-ink) hover:text-(--c-ink)"
              >
                Curriculum (PDF)
              </a>
              <span className={`${monoCls} flex gap-5 text-(--c-muted)`}>
                <a href={person.links.github} target="_blank" rel="noreferrer" className="hover:text-(--c-fg)">
                  GitHub ↗
                </a>
                <a href={person.links.linkedin} target="_blank" rel="noreferrer" className="hover:text-(--c-fg)">
                  LinkedIn ↗
                </a>
              </span>
            </div>
          </div>

          <figure className="col-span-4 md:col-span-4 md:col-start-9 md:self-end">
            <div className="relative">
              {/* Crop marks */}
              <span aria-hidden className="absolute -top-3 -left-3 h-3 w-3 border-t border-l border-(--c-muted)" />
              <span aria-hidden className="absolute -top-3 -right-3 h-3 w-3 border-t border-r border-(--c-muted)" />
              <span aria-hidden className="absolute -bottom-3 -left-3 h-3 w-3 border-b border-l border-(--c-muted)" />
              <span aria-hidden className="absolute -right-3 -bottom-3 h-3 w-3 border-r border-b border-(--c-muted)" />
              <DitherPortrait src={person.cutout} ink={INK} alt={`Portrait of ${person.name}`} />
            </div>
            <figcaption className={`${monoCls} mt-6 flex justify-between gap-4 text-(--c-muted)`}>
              <span>Fig. 1 — Portrait, 8×8 ordered dither</span>
              <span className="shrink-0 [@media(hover:none)]:hidden">Hover to develop</span>
              <span className="hidden shrink-0 [@media(hover:none)]:inline">Drag to develop</span>
            </figcaption>
          </figure>
        </section>

        {/* Now */}
        <div className={`${grid} ${monoCls} gap-y-1 border-y border-(--c-line) py-3`}>
          <span className="col-span-1 text-(--c-ink) md:col-span-1">Now</span>
          <span className="col-span-3 md:col-span-6">{currently.building}</span>
          <span className="col-span-3 col-start-2 text-(--c-muted) md:col-span-5 md:col-start-auto md:text-right">
            {currently.role}
          </span>
        </div>

        {/* Projects */}
        <section id="projects" className="py-20 md:py-32">
          <div className={`${grid} mb-14 items-end gap-y-3 md:mb-24`}>
            <span className={`${monoCls} col-span-1 text-(--c-muted)`}>01</span>
            <h2 className="col-span-3 text-[44px] leading-[0.9] font-medium tracking-[-0.045em] md:col-span-7 md:text-[76px]">
              Selected work
            </h2>
            <p className={`${monoCls} col-span-3 col-start-2 text-(--c-muted) md:col-span-4 md:col-start-auto md:text-right`}>
              Four projects — two in depth
            </p>
          </div>

          <div className={`${grid} gap-y-20 md:gap-y-32`}>
            <a
              href={featureA.href}
              target="_blank"
              rel="noreferrer"
              className={`group col-span-4 md:col-span-12 ${grid} gap-y-8`}
            >
              <div className="col-span-4 md:col-span-8">
                <ProjectImage project={featureA} aspect="aspect-video" sizes="(min-width: 768px) 62vw, 100vw" />
              </div>
              <div className="col-span-4 md:col-span-3 md:col-start-10 md:self-end">
                <ProjectMeta project={featureA} index={0} large />
              </div>
            </a>

            <a
              href={featureB.href}
              target="_blank"
              rel="noreferrer"
              className={`group col-span-4 md:col-span-12 ${grid} gap-y-8`}
            >
              <div className="order-2 col-span-4 md:order-1 md:col-span-3 md:self-start">
                <ProjectMeta project={featureB} index={1} large />
              </div>
              <div className="order-1 col-span-4 md:order-2 md:col-span-7 md:col-start-6">
                <ProjectImage project={featureB} aspect="aspect-video" sizes="(min-width: 768px) 55vw, 100vw" />
              </div>
            </a>

            {entries.map((project, i) => (
              <a
                key={project.slug}
                href={project.href}
                target="_blank"
                rel="noreferrer"
                className={`group col-span-4 flex flex-col gap-6 ${
                  i === 0 ? "md:col-span-4 md:col-start-2" : "md:col-span-4 md:col-start-8 md:mt-40"
                }`}
              >
                <ProjectImage project={project} aspect="aspect-3/2" sizes="(min-width: 768px) 30vw, 100vw" />
                <ProjectMeta project={project} index={i + 2} />
              </a>
            ))}
          </div>
        </section>

        <footer id="contact" className={`${grid} ${monoCls} gap-y-2 border-t border-(--c-line) py-6 text-(--c-muted)`}>
          <span className="col-span-4 md:col-span-6">POC C — Hybrid. Not linked from the live site.</span>
          <span className="col-span-4 flex gap-5 md:col-span-6 md:justify-end">
            <a href={person.links.github} className="hover:text-(--c-fg)">GitHub ↗</a>
            <a href={person.links.linkedin} className="hover:text-(--c-fg)">LinkedIn ↗</a>
            <a href={person.links.cv} className="hover:text-(--c-fg)">CV ↗</a>
          </span>
        </footer>
      </div>
    </div>
  );
}
