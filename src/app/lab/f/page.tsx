import type { Metadata } from "next";
import Image from "next/image";
import { currently, person } from "@/lab/content";
import { aiPractices, caseStudies, contactLine, entries, experience, marineWobbles } from "../e/_content";
import FoldingScreen from "./_components/FoldingScreen";
import LoopVideo from "./_components/LoopVideo";
import Phone from "./_components/Phone";

export const metadata: Metadata = {
  title: "Maria Bonete: full-stack developer",
  description:
    "Full-stack developer in Madrid, specialising in AI-driven engineering, web, React Native and Web3. Case studies, shipped projects, and how I work with coding agents.",
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
  showcase: React.ReactNode;
  // The engineering, for the projects that have it: a spec list and the decisions that prove it.
  proof?: { facts: { k: string; v: string }[]; highlights: { title: string; body: string }[] };
  links: { label: string; href: string; primary?: boolean; external?: boolean }[];
};

type Shot = { src: string; w: number; h: number; alt: string };

// A browser window with the address it was taken from: the live site, or the local build.
function Browser({ url, shot }: { url: string; shot: Shot }) {
  return (
    <div className="lf-browser">
      <div className="lf-browser-bar" aria-hidden>
        <span className="lf-browser-dots" />
        <span className="lf-browser-url">{url}</span>
      </div>
      <Image src={shot.src} width={shot.w} height={shot.h} alt={shot.alt} sizes="(max-width: 760px) 92vw, 52vw" />
    </div>
  );
}

// The site at desktop width, with the same page on a phone standing in front of its corner.
function Devices({ url, desktop, phone }: { url: string; desktop: Shot; phone?: Shot }) {
  return (
    <div className="lf-devices" data-phone={phone ? "" : undefined}>
      <Browser url={url} shot={desktop} />
      {phone && (
        <Phone>
          <Image src={phone.src} width={phone.w} height={phone.h} alt={phone.alt} sizes="(max-width: 760px) 26vw, 13vw" />
        </Phone>
      )}
    </div>
  );
}

const phoneShot = (name: string, alt: string): Shot => ({ src: `/lab/f/screens/${name}-phone.webp`, w: 585, h: 1170, alt });

// Every project gets the same treatment: one flat colour taken from its own palette, the real
// product on it, its name set large, and the same few facts.
const bands: Band[] = [
  {
    id: "marine-wobbles",
    title: marineWobbles.title,
    status: marineWobbles.status,
    summary: marineWobbles.summary,
    stack: marineWobbles.stack,
    ground: "#63bdea",
    tone: "light",
    showcase: (
      <div className="lf-phones">
        <Phone>
          <Image src="/lab/f/mw/board.webp" width={560} height={1120} alt="Level 2: a group of purple octopuses popping for 1,500 points on the six-by-six board." sizes="(max-width: 760px) 30vw, 14vw" />
        </Phone>
        <Phone size="lead">
          <LoopVideo src="/lab/f/mw/map-sakura.mp4" poster="/lab/f/mw/map-sakura.webp" label="The Sakura Waters map, its sea moving around the island path of levels." />
        </Phone>
        <Phone>
          <Image src="/lab/f/mw/urchins.webp" width={560} height={1120} alt="Level 66: urchins and patches to clear, with 55 moves left." sizes="(max-width: 760px) 30vw, 14vw" />
        </Phone>
      </div>
    ),
    proof: { facts: marineWobbles.facts, highlights: marineWobbles.highlights },
    links: [
      { label: "Read the case study", href: "/lab/f/work/marine-wobbles", primary: true },
      { label: "Watch the trailer", href: `https://www.youtube.com/watch?v=${marineWobbles.trailerId}`, external: true },
    ],
  },
  {
    id: "dwelltrace",
    title: dwelltrace.title,
    summary: dwelltrace.summary,
    stack: dwelltrace.stack.slice(0, 5),
    ground: "#b4492c",
    tone: "dark",
    showcase: <Devices url="localhost:3000" desktop={dwelltrace.image} />,
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
    showcase: (
      <Devices
        url="localhost:3000"
        desktop={{ src: "/lab/f/screens/homely-desktop.webp", w: 1262, h: 662, alt: "Homely's listings page: a search and sort panel beside cards for five homes." }}
      />
    ),
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
    showcase: (
      <div className="lf-phones">
        <Phone>
          <Image src="/lab/f/screens/bpm-tapping.webp" width={585} height={1170} alt="Tapping along: eleven beats in, the live reading says 128 BPM while the actual tempo stays hidden." sizes="(max-width: 760px) 30vw, 14vw" />
        </Phone>
        <Phone size="lead">
          <Image src="/lab/f/screens/bpm-phone.webp" width={585} height={1170} alt="A new round: The Beatles' Come Together, both BPM panels still empty." sizes="(max-width: 760px) 34vw, 17vw" />
        </Phone>
        <Phone>
          <Image src="/lab/f/screens/bpm-result.webp" width={585} height={1170} alt="Submitted: 124 BPM guessed against an actual 124, Nailed it!" sizes="(max-width: 760px) 30vw, 14vw" />
        </Phone>
      </div>
    ),
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
    ground: "#7c212f",
    tone: "dark",
    showcase: (
      <Devices
        url="the-coffee-place.vercel.app"
        desktop={{
          src: "/lab/f/screens/coffee-desktop.webp",
          w: 1600,
          h: 1000,
          alt: "The Coffee Place: \u201cSix staples. Collect the series.\u201d beside six sugar sachets, each printed in its own ink with a price and an add stamp.",
        }}
        phone={phoneShot("coffee", "The same page on a phone.")}
      />
    ),
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
            <a href="#experience">Experience</a>
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
          <ol className="lf-principles">
            {aiPractices.map((p) => (
              <li key={p.title}>
                <h3>{p.title}</h3>
                <p>
                  {p.text}
                  {p.example && <> {p.example}</>}
                </p>
              </li>
            ))}
          </ol>
          <p className="lf-built">
            <a href="/lab/e/built">How this site was built</a>
          </p>
        </section>

        <section id="work" aria-labelledby="work-h">
          <div className="lf-work-head">
            <h2 id="work-h">Work</h2>
            <p>An Android game in testing on Google Play, two web apps with full case studies, and two smaller projects.</p>
          </div>

          {bands.map((b) => (
            <article
              key={b.id}
              id={b.id}
              className="lf-band"
              data-tone={b.tone}
              data-proof={b.proof ? "" : undefined}
              style={{ "--band": b.ground } as React.CSSProperties}
              aria-labelledby={`${b.id}-h`}
            >
              <h3 id={`${b.id}-h`} className="lf-band-title">
                {b.title}
              </h3>
              <div className="lf-band-object">
                {b.showcase}
              </div>
              <div className="lf-band-copy">
                {b.status && <p className="lf-status">{b.status}</p>}
                <p className="lf-summary">{b.summary}</p>
                {b.proof && (
                  <dl className="lf-facts">
                    {b.proof.facts.map((f) => (
                      <div key={f.k}>
                        <dt>{f.k}</dt>
                        <dd>{f.v}</dd>
                      </div>
                    ))}
                  </dl>
                )}
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
              {b.proof && (
                <div className="lf-proof">
                  <ul className="lf-highlights">
                    {b.proof.highlights.map((h) => (
                      <li key={h.title}>
                        <h4>{h.title}</h4>
                        <p>{h.body}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </article>
          ))}
        </section>

        <section id="experience" className="lf-exp" aria-labelledby="exp-h">
          <h2 id="exp-h">Experience</h2>
          <ol className="lf-exp-list">
            {experience.map((x) => (
              <li key={x.id}>
                <p className="lf-exp-dates">{x.dates}</p>
                <div className="lf-exp-who">
                  <h3>{x.company}</h3>
                  <p>{x.role}</p>
                </div>
                <div className="lf-exp-what">
                  <ul>
                    {x.points.map((p) => (
                      <li key={p}>{p}</li>
                    ))}
                  </ul>
                  <p className="lf-exp-stack">{x.stack}</p>
                </div>
              </li>
            ))}
          </ol>
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
