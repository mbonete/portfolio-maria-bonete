import Link from "next/link";

const pocs = [
  { href: "/lab/a", name: "A — Instrument", note: "Minimal tech + terminal details, ⌘K palette" },
  { href: "/lab/b", name: "B — Immersive", note: "WebGL hero, scroll storytelling" },
  { href: "/lab/c", name: "C — Hybrid", note: "A's restraint + one shader moment" },
  { href: "/lab/d", name: "D — Drench", note: "Real subject over giant type, añil or almagre ground, four area tokens" },
  { href: "/lab/e", name: "E — Gold Screen", note: "Her shadow on a gold-leaf screen in a dark lacquer room, Blender render" },
];

export default function LabIndex() {
  return (
    <main className="mx-auto w-full max-w-xl px-4 py-16 font-mono text-sm">
      <h1 className="mb-8 text-neutral-400">/lab — revamp POCs</h1>
      <ul className="space-y-4">
        {pocs.map((p) => (
          <li key={p.href}>
            <Link href={p.href} className="underline underline-offset-4">
              {p.name}
            </Link>
            <p className="text-neutral-500">{p.note}</p>
          </li>
        ))}
      </ul>
    </main>
  );
}
