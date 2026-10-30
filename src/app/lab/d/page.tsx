import Image from "next/image";
import { projects } from "@/lab/content";
import Shell from "./_components/Shell";

const IMAGE: Record<string, string> = { homely: "/lab/d/homely.webp" };
const caseStudies = projects.filter((p) => p.kind === "case-study");
const entries = projects.filter((p) => p.kind === "entry");

export default async function LabD({ searchParams }: { searchParams: Promise<{ ground?: string }> }) {
  const { ground } = await searchParams;
  return (
    <Shell initialGround={ground === "red" ? "red" : "blue"}>
      <section id="projects" className="ld-work" aria-labelledby="ld-work-title">
        <h2 id="ld-work-title" className="ld-sr">
          Work
        </h2>

        <article id="marine-wobbles" className="ld-mw" aria-labelledby="ld-mw-title">
          <div className="ld-mw-giant" aria-hidden>
            <span>MARINE</span>
            <span>WOBBLES</span>
          </div>
          <Image
            src="/lab/d/mw-nautilus.webp"
            alt=""
            width={882}
            height={903}
            sizes="(min-width: 900px) 28vw, 58vw"
            className="ld-mw-nautilus"
          />
          <div className="ld-mw-phone">
            <video
              src="/lab/d/mw-map.mp4"
              poster="/lab/d/mw-map-poster.webp"
              muted
              loop
              playsInline
              autoPlay
              preload="none"
              aria-label="Marine Wobbles episode map, animated"
            />
          </div>
          <div className="ld-mw-copy">
            <h3 id="ld-mw-title">Marine Wobbles</h3>
            <p>
              A tap-to-pop match-3 for Android, built natively in Kotlin and Jetpack Compose. Its
              difficulty is measured, not guessed: five strategy bots play thousands of seeded games
              to tune every level.
            </p>
          </div>
          <dl className="ld-labels">
            <div>
              <dt>Levels</dt>
              <dd>80</dd>
            </div>
            <div>
              <dt>Painted episodes</dt>
              <dd>27</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>In development for Google Play</dd>
            </div>
          </dl>
        </article>

        {caseStudies.map((p, i) => (
          <article key={p.slug} className="ld-case" data-side={i % 2 ? "left" : "right"} aria-labelledby={`ld-${p.slug}`}>
            <div className="ld-case-giant" aria-hidden>
              {p.title.toUpperCase()}
            </div>
            <Image
              src={IMAGE[p.slug] ?? p.image}
              alt={`${p.title} landing page`}
              width={1280}
              height={IMAGE[p.slug] ? 686 : 720}
              sizes="(min-width: 900px) 56vw, 92vw"
              className="ld-case-img"
            />
            <div className="ld-case-copy">
              <h3 id={`ld-${p.slug}`}>
                <a href={p.href} target="_blank" rel="noreferrer">
                  {p.title}
                </a>
              </h3>
              <p>{p.summary}</p>
            </div>
            <p className="ld-labels ld-case-stack">{p.tags.join(" · ")}</p>
          </article>
        ))}

        <div className="ld-entries" aria-label="Earlier projects">
          {entries.map((p) => (
            <article key={p.slug} className="ld-entry" aria-labelledby={`ld-${p.slug}`}>
              <h3 id={`ld-${p.slug}`} className="ld-entry-title">
                <a href={p.href} target="_blank" rel="noreferrer">
                  {p.title}
                </a>
              </h3>
              <Image src={p.image} alt="" width={800} height={500} sizes="(min-width: 900px) 30vw, 70vw" className="ld-entry-img" />
              <p>{p.summary}</p>
            </article>
          ))}
        </div>
      </section>
    </Shell>
  );
}
