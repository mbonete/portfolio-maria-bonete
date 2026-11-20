import type { Metadata } from "next";
import Link from "next/link";
import { getArticles } from "@/blog";
import { person } from "@/content";
import PostList from "@/app/_components/PostList";
import { share } from "@/share";

const title = "Blog";
const description = "Articles on how I handle problems in my projects, from Google Play purchases to pacing a game's difficulty.";

export const metadata: Metadata = {
  title,
  description,
  ...share({ title, description, path: "/blog", image: "site" }),
};

export default function BlogPage() {
  return (
    <div className="lf lf-cs-page flex-1" style={{ "--band": "var(--paper)" } as React.CSSProperties}>
      <header className="lf-cs-top">
        <Link href="/#blog">Back to the site</Link>
      </header>

      <main>
        <section className="lf-cs-head lf-blog-index" aria-labelledby="blog-h">
          <h1 id="blog-h">Blog</h1>
          <PostList articles={getArticles()} heading="h2" />
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
