import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { caseStudies } from "@/content";
import CaseEnd from "@/app/_components/CaseEnd";
import CaseVideo from "@/app/_components/CaseVideo";

// The web case studies (Quote & Nod, Doorplate), in the same shape as Marine Wobbles': the project's colour
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
        <section className="lf-cs-head" aria-labelledby="cs-h">
          <h1 id="cs-h">{c.title}</h1>
          <p className="lf-cs-lede">{c.summary}</p>
          <CaseVideo
            id={c.videoId}
            title={`${c.title} demo`}
            label="Play the demo"
            seconds={c.videoLength}
            browser
            poster={
              <Image
                src={c.band.desktop.src}
                width={c.band.desktop.w}
                height={c.band.desktop.h}
                alt=""
                sizes="(max-width: 760px) 92vw, 90vw"
                loading="eager"
                fetchPriority="high"
              />
            }
          >
            {c.repo ? (
              <a href={c.repo} {...ext}>
                The code on GitHub
              </a>
            ) : (
              <span>The source is private.</span>
            )}
          </CaseVideo>
        </section>

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

        <CaseEnd slug={c.slug} />
      </main>
    </div>
  );
}
