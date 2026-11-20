import Image from "next/image";
import Link from "next/link";
import { aiIntro, aiPractices, caseStudies, entries, experience, marineWobbles, person } from "@/content";
import FoldingScreen from "./_components/FoldingScreen";
import LoopVideo from "./_components/LoopVideo";
import { BandVideo, CloseVideo } from "./_components/BandVideo";
import Devices from "./_components/Devices";
import Phone from "./_components/Phone";
import StickyTop from "./_components/StickyTop";


const ext = { target: "_blank", rel: "noreferrer" } as const;
const quoteAndNod = caseStudies.find((c) => c.slug === "quote-and-nod")!;
const doorplate = caseStudies.find((c) => c.slug === "doorplate")!;
const [bpm, coffee] = entries;

type Band = {
  id: string;
  title: string;
  kind: string; // its line in the Work index: what it is, and the stack that matters most
  status?: string;
  summary: string;
  stack: string[];
  ground: string;
  tone: "light" | "dark"; // the ink on the ground: dark ink on a light ground, or the reverse
  showcase: React.ReactNode;
  facts?: { k: string; v: string }[]; // a short spec list, for the project that has one
  links: { label: string; href: string; primary?: boolean; external?: boolean }[];
  video?: boolean; // the band has a demo that plays over its screens
};

// Every project gets the same treatment: one flat colour taken from its own palette, the real
// product on it, its name set large, and the same few facts.
const bands: Band[] = [
  {
    id: "marine-wobbles",
    title: marineWobbles.title,
    kind: "Android game · Kotlin, Jetpack Compose",
    status: marineWobbles.status,
    summary: marineWobbles.summary,
    stack: marineWobbles.stack,
    ground: "#63bdea",
    tone: "light",
    showcase: (
      <div className="lf-phones">
        <Phone>
          <LoopVideo src="/marine-wobbles/pop-loop.mp4" poster="/marine-wobbles/pop-loop.webp" label="Level 2: a big group of purple octopuses pops for 1,500 points and the board falls into place." />
        </Phone>
        <Phone size="lead">
          <LoopVideo src="/marine-wobbles/map-sakura.mp4" poster="/marine-wobbles/map-sakura.webp" label="The Sakura Waters map, its sea moving around the island path of levels." />
        </Phone>
        <Phone>
          <LoopVideo src="/marine-wobbles/level66-loop.mp4" poster="/marine-wobbles/level66-loop.webp" label="Level 66: groups popping as the urchin and patch goals fill up." />
        </Phone>
      </div>
    ),
    facts: marineWobbles.facts,
    links: [
      { label: "Read the case study", href: "/work/marine-wobbles", primary: true },
    ],
  },
  {
    id: "quote-and-nod",
    title: quoteAndNod.title,
    kind: "Web app · Next.js, Supabase",
    summary: quoteAndNod.summary,
    stack: quoteAndNod.stack.slice(0, 5),
    ground: quoteAndNod.band.ground,
    tone: quoteAndNod.band.tone,
    showcase: (
      <Devices
        video={{ id: quoteAndNod.videoId, title: "Quote & Nod demo", label: `Play the demo, ${quoteAndNod.videoLength} seconds` }}
        desktop={quoteAndNod.band.desktop}
        phone={quoteAndNod.band.phone}
      />
    ),
    links: [
      { label: "Read the case study", href: "/work/quote-and-nod", primary: true },
    ],
    video: true,
  },
  {
    id: "doorplate",
    title: doorplate.title,
    kind: "Web app · Next.js, SQLite",
    summary: doorplate.summary,
    stack: doorplate.stack.slice(0, 5),
    ground: doorplate.band.ground,
    tone: doorplate.band.tone,
    showcase: (
      <Devices
        video={{ id: doorplate.videoId, title: "Doorplate demo", label: `Play the demo, ${doorplate.videoLength} seconds` }}
        desktop={doorplate.band.desktop}
        phone={doorplate.band.phone}
      />
    ),
    links: [
      { label: "Read the case study", href: "/work/doorplate", primary: true },
      ...(doorplate.repo ? [{ label: "Code", href: doorplate.repo, external: true }] : []),
    ],
    video: true,
  },
  {
    id: "guess-the-bpm",
    title: bpm.title,
    kind: "Web game · React, TypeScript",
    summary: bpm.summary,
    stack: bpm.stack,
    ground: "#2b3ae0",
    tone: "dark",
    showcase: (
      <div className="lf-phones">
        <Phone>
          <Image src="/screens/bpm-tapping.webp" width={585} height={1170} alt="Tapping along: eleven beats in, the live reading says 128 BPM while the actual tempo stays hidden." sizes="(max-width: 760px) 30vw, 14vw" />
        </Phone>
        <Phone size="lead">
          <LoopVideo src="/screens/bpm-loop.mp4" poster="/screens/bpm-loop.webp" label="A round with The Beatles' Come Together: ten taps, a live reading of 83 BPM, and Nailed it! against the actual 83." />
        </Phone>
        <Phone>
          <Image src="/screens/bpm-result.webp" width={585} height={1170} alt="Submitted: 124 BPM guessed against an actual 124, Nailed it!" sizes="(max-width: 760px) 30vw, 14vw" />
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
    kind: "Website · Next.js",
    summary: coffee.summary,
    stack: coffee.stack,
    ground: "#7c212f",
    tone: "dark",
    showcase: (
      <Devices
        url="the-coffee-place.vercel.app"
        desktop={{
          src: "/screens/coffee-desktop.webp",
          w: 1600,
          h: 1000,
          alt: "The Coffee Place: \u201cSix staples. Collect the series.\u201d beside six sugar sachets, each printed in its own ink with a price and an add stamp.",
        }}
        phone={{
          loop: "/screens/coffee-loop.mp4",
          poster: "/screens/coffee-loop.webp",
          label: "The Coffee Place on a phone: four drinks stamped into the cart, the Cappuccino sachet opened into its page, then the order paid and its ticket stamped PAID.",
        }}
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
    <div className="lf flex-1">
      <section className="lf-hero" aria-labelledby="lf-name">
        <header className="lf-top">
          <div className="lf-top-bar">
            {/* Phones drop GitHub (Contact lists it), so the bar fits on one row. CV, GitHub and the
                contact link form one group, so when the bar wraps on a phone (a narrow screen or larger
                text) they move to a second row together. */}
            <nav aria-label="Primary" className="lf-nav">
              <a href="#work">Work</a>
              <a href="#ai">AI practice</a>
              <Link href="/blog" className="lf-nav-wide">Blog</Link>
              <a href="#experience">Experience</a>
              <span className="lf-top-actions">
                <a href={person.links.cv} {...ext}>
                  CV <span className="lf-sr">(PDF)</span>
                </a>
                <a href={person.links.github} className="lf-nav-wide" {...ext}>GitHub</a>
                {/* "Contact" on phones, as the section is called, so the bar stays on one row with larger text. */}
                <a className="lf-top-contact" href="#contact">
                  <span className="lf-top-contact-wide">Get in touch</span>
                  <span className="lf-top-contact-narrow">Contact</span>
                </a>
              </span>
            </nav>
          </div>
        </header>
        <StickyTop />

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
                  onete<span className="lf-tag">Working remotely<br />from Madrid</span>
                </span>
              </p>
            </>
          }
          intro={
            <div className="lf-intro">
              <p className="lf-role">
                <span className="lf-sr lf-role-who">
                  Full-stack developer<span className="lf-sr">, working remotely from Madrid.</span>{" "}
                </span>
                {/* Phones get the shorter list, under the role line they show. */}
                <span className="lf-role-wide">
                  Web and mobile (React Native and native Android), working with coding agents.
                </span>
                <span className="lf-role-narrow">Web, React Native and native Android, working with coding agents.</span>
              </p>
              <a className="lf-primary" href="#work">
                See the work
              </a>
            </div>
          }
        />
      </section>

      <main>
        <section id="work" aria-labelledby="work-h">
          {/* An index of the projects below, each with its band's colour, so a visitor can go straight to
              the one that matches the role. */}
          <div className="lf-work-head">
            <h2 id="work-h">Work</h2>
            <ol className="lf-index">
              {bands.map((b, i) => (
                <li key={b.id}>
                  <a href={`#${b.id}`}>
                    <span className="lf-index-n" aria-hidden>
                      <span className="lf-index-swatch" style={{ background: b.ground }} />
                      <span>{String(i + 1).padStart(2, "0")}</span>
                    </span>
                    <span className="lf-index-name">{b.title}</span>
                    <span className="lf-index-kind">{b.kind}</span>
                  </a>
                </li>
              ))}
            </ol>
          </div>

          {bands.map((b) => {
            const band = (
              <article
                key={b.id}
                id={b.id}
                className="lf-band"
                data-tone={b.tone}
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
                  {b.facts && (
                    <dl className="lf-facts">
                      {b.facts.map((f) => (
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
                      {b.links.map((l) =>
                        l.external ? (
                          <a key={l.label} href={l.href} className={l.primary ? "lf-link-strong" : undefined} {...ext}>
                            {l.label}
                          </a>
                        ) : (
                          <Link key={l.label} href={l.href} className={l.primary ? "lf-link-strong" : undefined}>
                            {l.label}
                          </Link>
                        ),
                      )}
                      {b.video && <CloseVideo />}
                    </div>
                  )}
                </div>
              </article>
            );
            return b.video ? <BandVideo key={b.id}>{band}</BandVideo> : band;
          })}
        </section>

        <section id="ai" className="lf-ai" aria-labelledby="ai-h">
          <div className="lf-ai-head">
            <h2 id="ai-h">Engineering, now with agents</h2>
            <p className="lf-ai-intro">{aiIntro}</p>
          </div>
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
            <Link href="/how-this-site-was-built">How this site was built</Link>
          </p>
          <p className="lf-repo">
            <a href={person.links.siteRepo} {...ext}>
              This site&apos;s code on GitHub
            </a>
            , with the instructions its agents follow.
          </p>
        </section>

        <section id="experience" className="lf-exp" aria-labelledby="exp-h">
          <h2 id="exp-h">Experience</h2>
          <p className="lf-exp-note">Every role below was remote.</p>
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
          <ul>
            <li>
              {/* The address itself, so a laptop without a mail app can still copy it. */}
              <a href={`mailto:${person.email}`}>{person.email}</a>
            </li>
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
