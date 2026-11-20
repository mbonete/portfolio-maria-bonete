import type { Metadata } from "next";
import Link from "next/link";
import { formatDate, getArticles } from "@/blog";
import { person } from "@/content";
import { ScreenImage } from "@/app/_components/Figure";
import { share } from "@/share";

const title = "Blog";
const description = "Articles on how I handle problems in my projects, from Google Play purchases to pacing a game's difficulty.";

export const metadata: Metadata = {
  title,
  description,
  ...share({ title, description, path: "/blog", image: "site" }),
};

// One row per article, newest first: its first game screen in the phone on its project's colour, then
// the title, date and reading time, the summary and the rules it covers.
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
            {getArticles().map((a, i) => (
              <li key={a.slug}>
                {a.lead && (
                  <Link
                    href={`/blog/${a.slug}`}
                    className="lf-bi-tile"
                    style={{ "--band": a.project.ground } as React.CSSProperties}
                    tabIndex={-1}
                    aria-hidden
                  >
                    <span className="lf-phone">
                      <span className="lf-phone-screen">
                        <ScreenImage figure={a.lead} sizes="(max-width: 760px) 36vw, 160px" priority={i === 0} />
                      </span>
                    </span>
                  </Link>
                )}
                <div className="lf-bi-text">
                  <h2>
                    <Link href={`/blog/${a.slug}`}>{a.title}</Link>
                  </h2>
                  <p className="lf-p-byline">
                    <time dateTime={a.date}>{formatDate(a.date)}</time>
                    <span aria-hidden> · </span>
                    {a.minutes} min read
                    <span aria-hidden> · </span>
                    {a.project.name}
                  </p>
                  <p className="lf-bi-summary">{a.summary}</p>
                  <ol className="lf-bi-rules" aria-label="The rules it covers">
                    {a.sections
                      .filter((s) => s.number)
                      .map((s) => (
                        <li key={s.id}>
                          <span className="lf-p-n">{s.number}</span>
                          {s.title}
                        </li>
                      ))}
                  </ol>
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
