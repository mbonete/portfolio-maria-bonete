import Image from "next/image";
import { person } from "@/lab/content";
import { ai, caseStudies, contactLine, entries, experience, marineWobbles } from "../_content";
import LightScreen from "./LightScreen";
import LightTrack from "./LightTrack";
import LoopVideo from "./LoopVideo";
import Toolkit from "./Toolkit";
import TransitionLink from "./TransitionLink";

const ext = { target: "_blank", rel: "noreferrer" } as const;

export default function Sections() {
  return (
    <main className="le-main">
      <section id="projects" className="le-sec" aria-labelledby="projects-h">
        <div className="le-sec-head">
          <h2 id="projects-h">Work</h2>
          <p>A game in development, two products taken apart as case studies, and two smaller builds.</p>
        </div>

        <article id="marine-wobbles" className="le-mw" aria-labelledby="mw-h">
          <div className="le-mw-media">
            <div className="le-mount le-phone">
              <LoopVideo
                src="/lab/d/mw-map.mp4"
                poster="/lab/d/mw-map-poster.webp"
                width={540}
                height={958}
                label="The painted episode map of Marine Wobbles, scrolling between levels."
              />
            </div>
            <Image className="le-mw-nautilus" src="/lab/d/mw-nautilus.webp" width={882} height={903} alt="" sizes="(max-width: 760px) 40vw, 260px" />
          </div>
          <div className="le-mw-copy">
            <h3 id="mw-h">{marineWobbles.title}</h3>
            <p className="le-status">{marineWobbles.status}</p>
            <p className="le-lede">{marineWobbles.summary}</p>
            <dl className="le-facts">
              {marineWobbles.facts.map((f) => (
                <div key={f.k}>
                  <dt>{f.k}</dt>
                  <dd>{f.v}</dd>
                </div>
              ))}
            </dl>
            <p className="le-stack">{marineWobbles.stack.join(" · ")}</p>
          </div>
        </article>

        {caseStudies.map((c, i) => (
          <article key={c.slug} id={c.slug} className="le-case" data-flip={i % 2 ? "" : undefined} aria-labelledby={`${c.slug}-h`}>
            <TransitionLink href={`/lab/e/work/${c.slug}`} className="le-mount le-case-media" aria-hidden tabIndex={-1}>
              <Image
                src={c.image.src}
                width={c.image.w}
                height={c.image.h}
                alt={c.image.alt}
                sizes="(max-width: 760px) 92vw, 52vw"
                style={{ viewTransitionName: `case-${c.slug}` }}
              />
            </TransitionLink>
            <div className="le-case-copy">
              <h3 id={`${c.slug}-h`}>
                <TransitionLink href={`/lab/e/work/${c.slug}`}>{c.title}</TransitionLink>
              </h3>
              <p className="le-lede">{c.summary}</p>
              <p className="le-stack">{c.stack.slice(0, 5).join(" · ")}</p>
              <div className="le-links">
                <TransitionLink href={`/lab/e/work/${c.slug}`} className="le-link-strong">
                  Read the case study
                </TransitionLink>
                <a href={`https://www.youtube.com/watch?v=${c.videoId}`} {...ext}>Watch the demo</a>
                {c.repo && <a href={c.repo} {...ext}>Code</a>}
              </div>
            </div>
          </article>
        ))}

        <ul className="le-entries" aria-label="Smaller builds">
          {entries.map((e) => (
            <li key={e.title}>
              <a href={e.live} {...ext} className="le-mount le-entry-media" aria-hidden tabIndex={-1}>
                <Image src={e.image.src} width={e.image.w} height={e.image.h} alt="" sizes="(max-width: 760px) 92vw, 30vw" />
              </a>
              <h3>{e.title}</h3>
              <p>{e.summary}</p>
              <p className="le-stack">{e.stack.join(" · ")}</p>
              <div className="le-links">
                <a href={e.live} {...ext}>Live site</a>
                <a href={e.repo} {...ext}>Code</a>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section id="ai" className="le-sec" aria-labelledby="ai-h">
        <div className="le-sec-head">
          <h2 id="ai-h">AI-driven engineering</h2>
        </div>
        <p className="le-stance">{ai.stance}</p>

        <h3 className="le-sub">Principles, each with a result I measured</h3>
        <ol className="le-principles">
          {ai.principles.map((p) => (
            <li key={p.title}>
              <h4>{p.title}</h4>
              <p>{p.body}</p>
              <p className="le-result">
                <span>Measured</span> {p.result}
              </p>
            </li>
          ))}
        </ol>

        <h3 className="le-sub">Toolkit</h3>
        <Toolkit items={ai.toolkit} />
        <p className="le-aside">
          This site is one worked example: <TransitionLink href="/lab/e/built">how it was built</TransitionLink>.
        </p>
      </section>

      <section id="experience" className="le-sec" aria-labelledby="exp-h">
        <div className="le-sec-head">
          <h2 id="exp-h">Experience</h2>
          <p>All remote.</p>
        </div>
        <ol className="le-roles">
          {experience.map((r) => (
            <li key={r.company} id={r.id}>
              <p className="le-dates">{r.dates}</p>
              <div>
                <h3>
                  {r.role} <span>at {r.company}</span>
                </h3>
                <ul>
                  {r.points.map((p) => (
                    <li key={p}>{p}</li>
                  ))}
                </ul>
                <p className="le-stack">{r.stack}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section id="about" className="le-sec le-about" aria-labelledby="about-h">
        <div className="le-sec-head">
          <h2 id="about-h">About</h2>
        </div>
        <div className="le-about-body">
          <p>
            I&apos;m a developer in Madrid. I build web and mobile products end to end, and I&apos;ve worked remotely since
            2022 across full-stack web, React Native, Web3 and, now, agent-driven engineering.
          </p>
          <p>
            Before software I studied Art History at the Complutense University of Madrid. Close looking is still most of
            my method: in an interface, in a pull request, and in whatever an agent hands back.
          </p>
        </div>
        <div className="le-about-side">
          <figure className="le-mount le-about-photo">
            <Image src={person.photo} width={430} height={448} alt="Maria Bonete, smiling, with long brown hair." sizes="260px" />
          </figure>
          <dl className="le-facts le-about-facts">
            <div>
              <dt>Based in</dt>
              <dd>Madrid, Spain</dd>
            </div>
            <div>
              <dt>Languages</dt>
              <dd>Spanish (native), English (C1)</dd>
            </div>
            <div>
              <dt>Education</dt>
              <dd>BA Art History, Complutense University of Madrid: Extraordinary Award (9.48/10)</dd>
            </div>
          </dl>
        </div>
      </section>

      {/* The page ends where it began: the screen again, under the same light. */}
      <section id="contact" className="le-sec le-contact" aria-labelledby="contact-h">
        <LightScreen echo />
        <div className="le-contact-head">
          <h2 id="contact-h">Contact</h2>
          <p>{contactLine}</p>
        </div>
        <div className="le-contact-end">
          <ul className="le-contact-links">
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
          <LightTrack />
        </div>
      </section>

      <footer className="le-foot">
        <p>Maria Bonete · Madrid</p>
        <p>
          <TransitionLink href="/lab/e/built">How this site was built</TransitionLink>
        </p>
      </footer>
    </main>
  );
}
