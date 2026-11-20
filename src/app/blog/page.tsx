import type { Metadata } from "next";
import Link from "next/link";
import { formatDate, getArticles } from "@/blog";
import { person } from "@/content";
import Figure from "@/app/_components/Figure";
import { share } from "@/share";

const title = "Blog";
const description = "Articles on how I handle problems in my projects, from Google Play purchases to pacing a game's difficulty.";

export const metadata: Metadata = {
  title,
  description,
  ...share({ title, description, path: "/blog", image: "site" }),
};

// The articles, newest first: each with its picture on its project's colour, then the title, the date
// and reading time, and the summary.
export default function BlogPage() {
  return (
    <div className="lf lf-cs-page flex-1" style={{ "--band": "var(--paper)" } as React.CSSProperties}>
      <header className="lf-cs-top">
        <Link href="/">Back to the site</Link>
      </header>

      <main>
        <section className="lf-bi" aria-labelledby="blog-h">
          <h1 id="blog-h">Blog</h1>
          <ol className="lf-bi-list">
            {getArticles().map((a) => (
              <li key={a.slug}>
                {a.hero && (
                  <Link
                    href={`/blog/${a.slug}`}
                    className="lf-bi-thumb"
                    style={{ "--band": a.project.ground } as React.CSSProperties}
                    tabIndex={-1}
                    aria-hidden
                  >
                    <Figure figure={a.hero} variant="thumb" />
                  </Link>
                )}
                <div className="lf-bi-text">
                  <h2>
                    <Link href={`/blog/${a.slug}`}>{a.title}</Link>
                  </h2>
                  <p className="lf-a-byline">
                    <time dateTime={a.date}>{formatDate(a.date)}</time>
                    <span aria-hidden> · </span>
                    {a.minutes} min read
                    <span aria-hidden> · </span>
                    {a.project.name}
                  </p>
                  <p className="lf-bi-summary">{a.summary}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <nav className="lf-cs-end" aria-label="More">
          <Link href="/#work">See the work</Link>
          <a href={`mailto:${person.email}`}>Email me</a>
          <a href={person.links.linkedin} target="_blank" rel="noreferrer">
            Talk to me on LinkedIn
          </a>
        </nav>
      </main>
    </div>
  );
}
