import Link from "next/link";
import type { Block, Inline } from "@/blog";
import Figure from "./Figure";

const ext = { target: "_blank", rel: "noreferrer" } as const;

function Parts({ parts }: { parts: Inline[] }) {
  return parts.map((p, i) => {
    if (p.kind === "strong") return <strong key={i}>{p.text}</strong>;
    if (p.kind === "code") return <code key={i}>{p.text}</code>;
    if (p.kind === "link")
      return p.href.startsWith("/") ? (
        <Link key={i} href={p.href}>
          {p.text}
        </Link>
      ) : (
        <a key={i} href={p.href} {...ext}>
          {p.text}
        </a>
      );
    return p.text;
  });
}

// An article's paragraphs, lists and figures.
export default function Prose({ blocks, className }: { blocks: Block[]; className?: string }) {
  return blocks.map((b, i) =>
    b.kind === "figure" ? (
      <Figure key={i} figure={b} variant="body" />
    ) : b.kind === "p" ? (
      <p key={i} className={className}>
        <Parts parts={b.parts} />
      </p>
    ) : (
      <ul key={i}>
        {b.items.map((item, j) => (
          <li key={j}>
            <Parts parts={item} />
          </li>
        ))}
      </ul>
    ),
  );
}
