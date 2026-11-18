import Link from "next/link";
import { caseStudies, marineWobbles, person } from "@/content";

const ext = { target: "_blank", rel: "noreferrer" } as const;

// The case studies in the order the home page shows them; the last leads back to the first.
const order = [
  { slug: "marine-wobbles", title: marineWobbles.title },
  ...caseStudies.map((c) => ({ slug: c.slug, title: c.title })),
];

// Every case study ends the same way: the next one, the CV, email and LinkedIn.
export default function CaseEnd({ slug }: { slug: string }) {
  const next = order[(order.findIndex((c) => c.slug === slug) + 1) % order.length];
  return (
    <nav className="lf-cs-end" aria-label="More">
      <Link href={`/work/${next.slug}`}>Next: {next.title}</Link>
      <a href={person.links.cv} {...ext}>
        CV (PDF)
      </a>
      <a href={`mailto:${person.email}`}>Email me</a>
      <a href={person.links.linkedin} {...ext}>
        Talk to me on LinkedIn
      </a>
    </nav>
  );
}
