import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { formatDate, getArticle, slugs } from "@/blog";
import { person } from "@/content";
import Prose from "@/app/_components/Prose";
import { share } from "@/share";

// An article in the case studies' shape: its project's colour at the head, then one section per rule.
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
      className="lf lf-cs-page lf-post flex-1"
      data-tone={a.project.tone}
      style={{ "--band": a.project.ground } as React.CSSProperties}
    >
      <header className="lf-cs-top">
        <Link href="/#blog">Back to the site</Link>
        <Link href="/blog">Blog</Link>
      </header>

      <main>
        <article>
          <header className="lf-cs-head">
            <p className="lf-post-meta">
              <time dateTime={a.date}>{formatDate(a.date)}</time> · {a.project.name}
            </p>
            <h1>{a.title}</h1>
            <Prose blocks={a.intro} className="lf-cs-lede" />
          </header>

          {a.sections.map((s) => (
            <section key={s.id} className="lf-cs-sec" aria-labelledby={s.id}>
              <h2 id={s.id}>{s.title}</h2>
              <div className="lf-cs-body">
                <Prose blocks={s.blocks} />
              </div>
            </section>
          ))}
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
