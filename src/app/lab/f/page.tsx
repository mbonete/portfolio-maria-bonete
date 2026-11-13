import type { Metadata } from "next";
import Image from "next/image";
import { currently, person } from "@/lab/content";
import { ai, caseStudies, contactLine, entries, marineWobbles } from "../e/_content";
import FoldingScreen from "./_components/FoldingScreen";

export const metadata: Metadata = {
  title: "Maria Bonete: full-stack developer",
  description:
    "Full-stack developer in Madrid, specialising in AI-driven engineering, web, React Native and Web3. A measured AI practice, shipped work and case studies.",
};

const ext = { target: "_blank", rel: "noreferrer" } as const;
const dwelltrace = caseStudies.find((c) => c.slug === "dwelltrace")!;
const homely = caseStudies.find((c) => c.slug === "homely")!;
const [bpm, coffee] = entries;

type Band = {
  id: string;
  title: string;
  status?: string;
  summary: string;
  stack: string[];
  ground: string;
  tone: "light" | "dark"; // the ink on the ground: dark ink on a light ground, or the reverse
  object: { src: string; w: number; h: number; alt: string; cut?: boolean; spread?: boolean };
  links: { label: string; href: string; primary?: boolean; external?: boolean }[];
};

// Every project gets the same treatment: one flat colour taken from its own palette, one object, its
// name set large, and the same few facts. The subjects differ; the formula holds them together.
const bands: Band[] = [
  {
    id: "marine-wobbles",
    title: marineWobbles.title,
    status: marineWobbles.status,
    summary: marineWobbles.summary,
    stack: marineWobbles.stack,
    ground: "#63bdea",
    tone: "light",
    object: {
      src: "/lab/d/mw-nautilus.webp",
      w: 882,
      h: 903,
      alt: "A glossy, inflated purple nautilus shell from the game's art.",
      cut: true,
    },
    links: [],
  },
  {
    id: "dwelltrace",
    title: dwelltrace.title,
    summary: dwelltrace.summary,
    stack: dwelltrace.stack.slice(0, 5),
    ground: "#b4492c",
    tone: "dark",
    object: dwelltrace.image,
    links: [
      { label: "Read the case study", href: "/lab/e/work/dwelltrace", primary: true },
      { label: "Watch the demo", href: `https://www.youtube.com/watch?v=${dwelltrace.videoId}`, external: true },
    ],
  },
  {
    id: "homely",
    title: homely.title,
    summary: homely.summary,
    stack: homely.stack.slice(0, 5),
    ground: "#1f6b4c",
    tone: "dark",
    object: homely.image,
    links: [
      { label: "Read the case study", href: "/lab/e/work/homely", primary: true },
      { label: "Watch the demo", href: `https://www.youtube.com/watch?v=${homely.videoId}`, external: true },
      ...(homely.repo ? [{ label: "Code", href: homely.repo, external: true }] : []),
    ],
  },
  {
    id: "guess-the-bpm",
    title: bpm.title,
    summary: bpm.summary,
    stack: bpm.stack,
    ground: "#2b3ae0",
    tone: "dark",
    object: { ...bpm.image, alt: "Three phone screens of Guess The BPM: a song playing, a guess, and the result.", cut: true },
    links: [
      { label: "Open the live site", href: bpm.live, primary: true, external: true },
      { label: "Code", href: bpm.repo, external: true },
    ],
  },
  {
    id: "the-coffee-place",
    title: coffee.title,
    summary: coffee.summary,
    stack: coffee.stack,
    ground: "#b8d88a",
    tone: "light",
    object: {
      src: "/the-coffee-place-sachets.webp",
      w: 1800,
      h: 1265,
      alt: "The six sugar sachets of The Coffee Place scattered on its pistachio table, each printed in its own ink: espresso, americano, cappuccino, iced latte, caramel macchiato and filter coffee.",
      cut: true,
      spread: true,
    },
    links: [
      { label: "Open the live site", href: coffee.live, primary: true, external: true },
      { label: "Code", href: coffee.repo, external: true },
    ],
  },
];

export default function LabF() {
  return (
    <div className="lf">
      <section className="lf-hero" aria-labelledby="lf-name">
        <header className="lf-top">
          <nav aria-label="Primary" className="lf-nav">
            <a href="#work">Work</a>
            <a href="#ai">AI practice</a>
            <a href={person.links.cv} {...ext}>
              CV <span className="lf-sr">(PDF)</span>
            </a>
            <a href={person.links.github} {...ext}>GitHub</a>
          </nav>
          <a className="lf-top-contact" href="#contact">
            Get in touch
          </a>
        </header>

        <FoldingScreen
          name={
            <>
              <h1 id="lf-name" className="lf-name">
                Maria Bonete
              </h1>
              {/* The same name again, invisible, so two facts can sit in the space above its small
                  letters, wherever the letters fall. */}
              <p className="lf-name lf-name-ghost" aria-hidden>
                M
                <span className="lf-tuck">
                  aria<span className="lf-tag">Full-stack<br />developer</span>
                </span>{" "}
                B
                <span className="lf-tuck">
                  onete<span className="lf-tag">Madrid, now<br />at {currently.company}</span>
                </span>
              </p>
            </>
          }
          intro={
            <div className="lf-intro">
              <p className="lf-role">
                <span className="lf-sr">Full-stack developer in Madrid, now at {currently.company}. </span>
                {/* Non-breaking hyphen keeps "AI-driven" on one line. */}
                Specialising in AI{"\u2011"}driven engineering, web, React Native and Web3.
              </p>
              <a className="lf-primary" href="#work">
                See the work
              </a>
            </div>
          }
        />
      </section>

      <main>
        <section id="ai" className="lf-ai" aria-labelledby="ai-h">
          <h2 id="ai-h">AI-driven engineering</h2>
          <p className="lf-stance">{ai.stance}</p>
          <ol className="lf-principles">
            {ai.principles.map((p) => (
              <li key={p.title}>
                <h3>{p.title}</h3>
                <p>{p.result}</p>
              </li>
            ))}
          </ol>
          <p className="lf-built">
            This portfolio was designed and built with agents, the same way.{" "}
            <a href="/lab/e/built">How this site was built</a>
          </p>
          <p className="lf-aside">
            The full practice, with the toolkit, is on <a href="/lab/e#ai">the Gold Screen page</a>.
          </p>
        </section>

        <section id="work" aria-labelledby="work-h">
          <div className="lf-work-head">
            <h2 id="work-h">Work</h2>
            <p>A game in development, two products taken apart as case studies, and two smaller builds.</p>
          </div>

          {bands.map((b) => (
            <article
              key={b.id}
              id={b.id}
              className="lf-band"
              data-tone={b.tone}
              data-cut={b.object.cut || undefined}
              data-spread={b.object.spread || undefined}
              style={{ "--band": b.ground } as React.CSSProperties}
              aria-labelledby={`${b.id}-h`}
            >
              <h3 id={`${b.id}-h`} className="lf-band-title">
                {b.title}
              </h3>
              <div className="lf-band-object">
                <Image
                  src={b.object.src}
                  width={b.object.w}
                  height={b.object.h}
                  alt={b.object.alt}
                  sizes="(max-width: 760px) 92vw, 56vw"
                />
              </div>
              <div className="lf-band-copy">
                {b.status && <p className="lf-status">{b.status}</p>}
                <p className="lf-summary">{b.summary}</p>
                <p className="lf-stack">{b.stack.join(" · ")}</p>
                {b.links.length > 0 && (
                  <div className="lf-links">
                    {b.links.map((l) => (
                      <a key={l.label} href={l.href} className={l.primary ? "lf-link-strong" : undefined} {...(l.external ? ext : {})}>
                        {l.label}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </article>
          ))}
        </section>

        <section id="contact" className="lf-contact" aria-labelledby="contact-h">
          <h2 id="contact-h">Contact</h2>
          <p>{contactLine}</p>
          <ul>
            <li>
              <a href={person.links.linkedin} {...ext}>LinkedIn</a>
            </li>
            <li>
              <a href={person.links.github} {...ext}>GitHub</a>
            </li>
            <li>
              <a href={person.links.cv} {...ext}>CV (PDF)</a>
            </li>
          </ul>
        </section>
      </main>

      <footer className="lf-end">
        <p>Maria Bonete · Madrid</p>
      </footer>
    </div>
  );
}
