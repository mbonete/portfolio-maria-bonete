import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { caseStudies, person } from "@/content";
import { BandVideo, CloseVideo } from "@/app/_components/BandVideo";
import Devices from "@/app/_components/Devices";

// The web case studies (Quote & Nod, Homely), in the same shape as Marine Wobbles': the project's colour
// with its screens and demo, then the engineering in plain sections.
export function generateStaticParams() {
  return caseStudies.map((c) => ({ slug: c.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const c = caseStudies.find((x) => x.slug === slug);
  return c ? { title: `${c.title}: case study`, description: c.summary } : {};
}

const ext = { target: "_blank", rel: "noreferrer" } as const;

export default async function CaseStudyPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const c = caseStudies.find((x) => x.slug === slug);
  if (!c) notFound();

  return (
    <div
      className="lf lf-cs-page flex-1"
      data-tone={c.band.tone}
      style={{ "--band": c.band.ground } as React.CSSProperties}
    >
      <header className="lf-cs-top">
        <Link href={`/#${c.slug}`}>Back to work</Link>
        <span>Case study</span>
      </header>

      <main>
        <BandVideo>
          <section className="lf-cs-head" aria-labelledby="cs-h">
            <h1 id="cs-h">{c.title}</h1>
            <p className="lf-cs-lede">{c.summary}</p>
            <div className="lf-cs-showcase">
              <Devices
                video={{ id: c.videoId, title: `${c.title} demo`, label: `Play the demo, ${c.videoLength} seconds` }}
                url="localhost:3000"
                desktop={c.band.desktop}
                phone={c.band.phone}
              />
            </div>
            <p className="lf-cs-links">
              <CloseVideo />
              {c.repo ? (
                <a href={c.repo} {...ext}>
                  The code on GitHub
                </a>
              ) : (
                <span>The source is private.</span>
              )}
            </p>
          </section>
        </BandVideo>

        <section className="lf-cs-sec" aria-labelledby="does">
          <h2 id="does">What it does</h2>
          <div className="lf-cs-body">
            <p>{c.problem}</p>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="built">
          <h2 id="built">What I built</h2>
          <div className="lf-cs-body">
            <ul className="lf-cs-points">
              {c.built.map((b) => (
                <li key={b}>{b}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="decisions">
          <h2 id="decisions">Decisions worth a look</h2>
          <div className="lf-cs-body">
            <ul className="lf-cs-points">
              {c.decisions.map((d) => (
                <li key={d.title}>
                  <strong>{d.title}.</strong> {d.body}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="model">
          <h2 id="model">Data model</h2>
          <div className="lf-cs-body">
            <p>{c.model}</p>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="stack">
          <h2 id="stack">Stack</h2>
          <div className="lf-cs-body">
            <p className="lf-cs-stack">{c.stack.join(" · ")}</p>
          </div>
        </section>

        <nav className="lf-cs-end" aria-label="More">
          <Link href="/#work">Back to all the work</Link>
          <a href={person.links.linkedin} {...ext}>
            Talk to me on LinkedIn
          </a>
        </nav>
      </main>
    </div>
  );
}
