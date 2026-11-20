import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { formatDate, getArticle, slugs } from "@/blog";
import { person } from "@/content";
import Figure from "@/app/_components/Figure";
import Prose from "@/app/_components/Prose";
import { share } from "@/share";

// An article: its project's colour at the head with the title, intro and a picture, then the rules in
// one reading column with a list of them alongside, to jump between.
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

export default async function ArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const a = getArticle((await params).slug);
  if (!a) notFound();

  return (
    <div
      className="lf lf-cs-page lf-a flex-1"
      data-tone={a.project.tone}
      style={{ "--band": a.project.ground } as React.CSSProperties}
    >
      <header className="lf-cs-top">
        <Link href="/">Back to the site</Link>
        <Link href="/blog">Blog</Link>
      </header>

      <main>
        <article>
          <header className="lf-a-head">
            <div className="lf-a-head-text">
              <h1>{a.title}</h1>
              <p className="lf-a-byline">
                <time dateTime={a.date}>{formatDate(a.date)}</time>
                <span aria-hidden> · </span>
                {a.minutes} min read
                <span aria-hidden> · </span>
                <Link href={a.project.href}>{a.project.name}</Link>
              </p>
              <Prose blocks={a.intro} className="lf-a-lede" />
            </div>
            {a.hero && <Figure figure={a.hero} variant="hero" />}
          </header>

          <div className="lf-a-layout">
            <nav className="lf-a-toc" aria-labelledby="toc-h">
              <p id="toc-h">In this article</p>
              <ol>
                {a.sections.map((s) => (
                  <li key={s.id}>
                    <a href={`#${s.id}`}>{s.title}</a>
                  </li>
                ))}
              </ol>
            </nav>

            <div className="lf-a-body">
              {a.sections.map((s) => (
                <section key={s.id} aria-labelledby={s.id}>
                  <h2 id={s.id}>{s.title}</h2>
                  <Prose blocks={s.blocks} />
                </section>
              ))}
            </div>
          </div>
        </article>

        <nav className="lf-cs-end" aria-label="More">
          <Link href="/blog">All articles</Link>
          <Link href={a.project.href}>The {a.project.name} case study</Link>
          <a href={`mailto:${person.email}`}>Email me</a>
        </nav>
      </main>
    </div>
  );
}
