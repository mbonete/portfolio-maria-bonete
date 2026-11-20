import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { formatDate, getArticle, slugs, type Figure } from "@/blog";
import { person } from "@/content";
import ArticleStage from "@/app/_components/ArticleStage";
import { ScreenImage } from "@/app/_components/Figure";
import Prose from "@/app/_components/Prose";
import { share } from "@/share";

// An article read beside the game: on wide screens a phone on the project's colour stays in view and
// shows the screen of the rule being read; on phones each rule's screen sits above its text.
export const dynamicParams = false;

export function generateStaticParams() {
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const a = getArticle((await params).slug);
  if (!a) return {};
  return {
    title: a.title,
    description: a.summary,
    ...share({ title: a.title, description: a.summary, path: `/blog/${a.slug}`, image: "marine-wobbles" }),
  };
}

// A rule's screen for phones: the top of the phone rising from a band of the project's colour, where
// the game shows its message, with the caption under the band.
function Shot({ figure, eager }: { figure: Figure; eager?: boolean }) {
  return (
    <figure className="lf-p-shot">
      <div className="lf-p-shot-band">
        <div className="lf-phone">
          <div className="lf-phone-screen">
            <ScreenImage figure={figure} sizes="(max-width: 899px) 72vw, 1px" eager={eager} />
          </div>
        </div>
      </div>
      {figure.caption && <figcaption>{figure.caption}</figcaption>}
    </figure>
  );
}

export default async function ArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const a = getArticle((await params).slug);
  if (!a) notFound();

  // The screens in order, and which one each section shows: its own, or the last one before it.
  const screens = a.sections.flatMap((s) => (s.screen ? [s.screen] : []));
  const stageSections = a.sections.map((s, i) => {
    const shown = a.sections.slice(0, i + 1).findLast((x) => x.screen)?.screen;
    return { id: s.id, screen: shown ? screens.indexOf(shown) : 0 };
  });

  return (
    <div className="lf lf-p flex-1" data-tone={a.project.tone} style={{ "--band": a.project.ground } as React.CSSProperties}>
      <main className="lf-p-grid">
        <div className="lf-p-read">
          <header className="lf-p-top">
            <Link href="/blog">Back to the blog</Link>
            <Link href="/">Maria Bonete</Link>
          </header>

          <article>
            <header className="lf-p-head">
              <h1>{a.title}</h1>
              <p className="lf-p-byline">
                <time dateTime={a.date}>{formatDate(a.date)}</time>
                <span aria-hidden> · </span>
                {a.minutes} min read
                <span aria-hidden> · </span>
                <Link href={a.project.href}>{a.project.name}</Link>
              </p>
              <Prose blocks={a.intro} className="lf-p-intro" />
            </header>

            <nav className="lf-p-toc" aria-labelledby="toc-h">
              <p id="toc-h">In this article</p>
              <ol>
                {a.sections.map((s) => (
                  <li key={s.id}>
                    <a href={`#${s.id}`}>
                      <span className="lf-p-n">{s.number}</span>
                      {s.title}
                    </a>
                  </li>
                ))}
              </ol>
            </nav>

            {a.sections.map((s) => (
              <section key={s.id} className="lf-p-sec" aria-labelledby={s.id}>
                <h2 id={s.id}>
                  {s.number && (
                    <span className="lf-p-n">
                      {s.number}
                      <span className="lf-sr">.</span>
                    </span>
                  )}
                  {s.title}
                </h2>
                {s.screen && <Shot figure={s.screen} eager={s.screen === a.lead} />}
                <div className="lf-p-text">
                  <Prose blocks={s.blocks} />
                </div>
              </section>
            ))}
          </article>
        </div>

        {screens.length > 0 && (
          <aside className="lf-p-stage" aria-label="Screens from the game">
            <ArticleStage
              sections={stageSections}
              captions={screens.map((f) => f.caption ?? "")}
              rules={a.sections.flatMap((s) => (s.number ? [{ id: s.id, number: s.number, title: s.title }] : []))}
            >
              {screens.map((f, i) => (
                <ScreenImage key={f.src} figure={f} sizes="(max-width: 899px) 1px, 300px" eager={i === 0} />
              ))}
            </ArticleStage>
          </aside>
        )}
      </main>

      <nav className="lf-cs-end" aria-label="More">
        <Link href="/blog">All articles</Link>
        <Link href={a.project.href}>The {a.project.name} case study</Link>
        <a href={`mailto:${person.email}`}>Email me</a>
      </nav>
    </div>
  );
}
