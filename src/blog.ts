import { readFileSync } from "node:fs";
import path from "node:path";

// The blog's articles, newest first. Each one's text is a Markdown file in src/articles, written in a
// small subset: one "# " title, "## " sections, paragraphs, "- " lists, [links](url), **bold** and
// `code`. The title and sections come from the file; the date and summary live here.
const index = [
  {
    slug: "marine-wobbles-difficulty",
    date: "2026-11-20",
    summary: "The six rules that pace the difficulty of Marine Wobbles' 80 levels, and the research each one follows.",
    project: "marine-wobbles",
  },
  {
    slug: "google-play-purchases",
    date: "2026-11-20",
    summary: "The five rules Marine Wobbles follows so a Google Play purchase is never lost or granted twice, with no server.",
    project: "marine-wobbles",
  },
] as const;

// The project an article is about: its name, its case study, and its colour from the home page, which
// the article's head carries.
const projects = {
  "marine-wobbles": { name: "Marine Wobbles", href: "/work/marine-wobbles", ground: "#63bdea", tone: "light" },
} as const;

export type Inline =
  | { kind: "text"; text: string }
  | { kind: "strong"; text: string }
  | { kind: "code"; text: string }
  | { kind: "link"; text: string; href: string };

export type Block = { kind: "p"; parts: Inline[] } | { kind: "ul"; items: Inline[][] };

export type Article = {
  slug: string;
  date: string;
  summary: string;
  title: string;
  project: (typeof projects)[keyof typeof projects];
  intro: Block[];
  sections: { id: string; title: string; blocks: Block[] }[];
};

export const slugs = index.map((a) => a.slug);

export function getArticle(slug: string): Article | undefined {
  const entry = index.find((a) => a.slug === slug);
  if (!entry) return undefined;
  const source = readFileSync(path.join(process.cwd(), "src/articles", `${slug}.md`), "utf8");
  return { ...entry, project: projects[entry.project], ...parse(source) };
}

export function getArticles(): Article[] {
  return index.map((a) => getArticle(a.slug)!);
}

export function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }).format(
    new Date(date),
  );
}

function parse(source: string) {
  let title = "";
  const intro: Block[] = [];
  const sections: Article["sections"] = [];
  // Paragraphs and lists are runs of lines between blank lines.
  let run: string[] = [];
  const flush = () => {
    if (!run.length) return;
    const blocks = sections.length ? sections[sections.length - 1].blocks : intro;
    blocks.push(
      run.every((l) => l.startsWith("- "))
        ? { kind: "ul", items: run.map((l) => inline(l.slice(2))) }
        : { kind: "p", parts: inline(run.join(" ")) },
    );
    run = [];
  };
  for (const raw of source.split("\n")) {
    const line = raw.trim();
    if (line.startsWith("# ")) {
      flush();
      title = line.slice(2);
    } else if (line.startsWith("## ")) {
      flush();
      const heading = line.slice(3);
      sections.push({ id: headingId(heading), title: heading, blocks: [] });
    } else if (line === "") {
      flush();
    } else {
      run.push(line);
    }
  }
  flush();
  if (!title) throw new Error("An article needs a '# ' title.");
  return { title, intro, sections };
}

// "1. Grant coins only for paid purchases" -> "grant-coins-only-for-paid-purchases"
function headingId(heading: string) {
  return heading
    .replace(/^\d+\.\s*/, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

// Links are scanned by hand, because addresses such as DOIs can hold their own brackets.
function inline(text: string): Inline[] {
  const parts: Inline[] = [];
  let plain = "";
  const push = (part: Inline) => {
    if (plain) parts.push({ kind: "text", text: plain });
    plain = "";
    parts.push(part);
  };
  let i = 0;
  while (i < text.length) {
    if (text[i] === "[") {
      const close = text.indexOf("](", i);
      if (close > i) {
        let depth = 1;
        let j = close + 2;
        for (; j < text.length && depth > 0; j++) {
          if (text[j] === "(") depth++;
          else if (text[j] === ")") depth--;
        }
        if (depth === 0) {
          push({ kind: "link", text: text.slice(i + 1, close), href: text.slice(close + 2, j - 1) });
          i = j;
          continue;
        }
      }
    }
    if (text.startsWith("**", i)) {
      const end = text.indexOf("**", i + 2);
      if (end > i) {
        push({ kind: "strong", text: text.slice(i + 2, end) });
        i = end + 2;
        continue;
      }
    }
    if (text[i] === "`") {
      const end = text.indexOf("`", i + 1);
      if (end > i) {
        push({ kind: "code", text: text.slice(i + 1, end) });
        i = end + 1;
        continue;
      }
    }
    plain += text[i];
    i++;
  }
  if (plain) parts.push({ kind: "text", text: plain });
  return parts;
}
