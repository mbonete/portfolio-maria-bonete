import Link from "next/link";
import { formatDate, type Article } from "@/blog";

// One row per article, laid out like Experience: the date in the margin, the title with its project,
// then the summary. The titles are h3 under the home page's "Blog" heading, and h2 on the blog's page.
export default function PostList({ articles, heading: H = "h3" }: { articles: Article[]; heading?: "h2" | "h3" }) {
  return (
    <ol className="lf-posts">
      {articles.map((a) => (
        <li key={a.slug}>
          <p className="lf-posts-date">
            <time dateTime={a.date}>{formatDate(a.date)}</time>
          </p>
          <div className="lf-posts-title">
            <H>
              <Link href={`/blog/${a.slug}`}>{a.title}</Link>
            </H>
            <p>{a.project.name}</p>
          </div>
          <p className="lf-posts-summary">{a.summary}</p>
        </li>
      ))}
    </ol>
  );
}
