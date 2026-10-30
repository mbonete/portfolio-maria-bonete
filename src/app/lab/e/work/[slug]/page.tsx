import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import { caseStudies } from "../../_content";
import ContactStrip from "../../_components/ContactStrip";
import TransitionLink from "../../_components/TransitionLink";

export function generateStaticParams() {
  return caseStudies.map((c) => ({ slug: c.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const c = caseStudies.find((x) => x.slug === slug);
  return c ? { title: `${c.title}: case study`, description: c.summary } : { title: "Case study" };
}

const ext = { target: "_blank", rel: "noreferrer" } as const;

export default async function CaseStudyPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const c = caseStudies.find((x) => x.slug === slug);
  if (!c) notFound();
  const other = caseStudies.find((x) => x.slug !== slug)!;

  return (
    <div className="le le-page">
      <header className="le-page-top">
        <TransitionLink href={`/lab/e#${c.slug}`} className="le-back">
          Back to work
        </TransitionLink>
        <span className="le-page-crumb">Case study</span>
      </header>

      <main className="le-cs">
        <div className="le-cs-head">
          <h1>{c.title}</h1>
          <p className="le-lede">{c.summary}</p>
          <div className="le-links">
            <a href={`https://www.youtube.com/watch?v=${c.videoId}`} {...ext} className="le-link-strong">
              Watch the demo
            </a>
            {c.repo && (
              <a href={c.repo} {...ext}>
                Code on GitHub
              </a>
            )}
          </div>
        </div>

        <figure className="le-mount le-cs-hero">
          <Image
            src={c.image.src}
            width={c.image.w}
            height={c.image.h}
            alt={c.image.alt}
            sizes="(max-width: 760px) 92vw, 70vw"
            priority
            style={{ viewTransitionName: `case-${c.slug}` }}
          />
        </figure>

        <section className="le-cs-block" aria-labelledby="problem">
          <h2 id="problem">The problem</h2>
          <p>{c.problem}</p>
        </section>

        <section className="le-cs-block" aria-labelledby="built">
          <h2 id="built">What I built</h2>
          <ul className="le-cs-list">
            {c.built.map((b) => (
              <li key={b}>{b}</li>
            ))}
          </ul>
        </section>

        <section className="le-cs-block" aria-labelledby="decisions">
          <h2 id="decisions">Decisions worth a look</h2>
          <div className="le-cs-decisions">
            {c.decisions.map((d) => (
              <div key={d.title}>
                <h3>{d.title}</h3>
                <p>{d.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="le-cs-block" aria-labelledby="model">
          <h2 id="model">Data model</h2>
          <p>{c.model}</p>
        </section>

        <section className="le-cs-block" aria-labelledby="stack">
          <h2 id="stack">Stack</h2>
          <p className="le-stack le-stack-lg">{c.stack.join(" · ")}</p>
        </section>

        <nav className="le-cs-next" aria-label="Next case study">
          <TransitionLink href={`/lab/e/work/${other.slug}`}>
            <span>Next case study</span>
            {other.title}
          </TransitionLink>
        </nav>

        <ContactStrip />
      </main>
    </div>
  );
}
