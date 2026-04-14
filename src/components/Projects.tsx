type Project = {
  title: string;
  description: string;
  tags: string[];
  href: string;
};

const projects: Project[] = [
  {
    title: "The Coffee Place",
    description:
      "Showcases the artistry of a fictional coffee shop, letting users explore offerings and place orders.",
    tags: ["Next.js", "JavaScript", "Styled Components"],
    href: "https://the-coffee-place.vercel.app/",
  },
  {
    title: "Mago del Regalo",
    description:
      "AI-powered app that eliminates the challenge of finding gift ideas.",
    tags: ["Next.js", "TypeScript", "MaterialUI", "React Query"],
    href: "https://www.magodelregalo.com",
  },
  {
    title: "Guess The BPM",
    description:
      "A web-based game where users guess the beats per minute of a song. YouTube API integration with i18n support.",
    tags: ["React", "Styled Components"],
    href: "https://www.guess-the-bpm.com",
  },
  {
    title: "Homely",
    description:
      "A minimal real estate platform built as a proof of concept for integration with a CRUD API.",
    tags: ["React", "React Hook Form", "React Query", "MaterialUI"],
    href: "https://github.com/mbonete/homely",
  },
];

export default function Projects() {
  return (
    <section id="projects" className="py-20 border-t border-neutral-200 dark:border-neutral-800">
      <h2 className="text-2xl font-semibold tracking-tight mb-6 flex items-center gap-3">
        <span aria-hidden className="inline-block h-5 w-1.5 rounded-sm bg-primary" />
        Projects
      </h2>
      <div className="grid sm:grid-cols-2 gap-5">
        {projects.map((p) => (
          <a
            key={p.title}
            href={p.href}
            target="_blank"
            rel="noreferrer"
            className="group rounded-xl border border-neutral-200 dark:border-neutral-800 p-5 bg-background/40 backdrop-blur-sm hover:border-primary/60 hover:shadow-[0_0_30px_-10px_var(--color-primary)] transition"
          >
            <h3 className="font-medium group-hover:translate-x-0.5 transition-transform">
              {p.title}
            </h3>
            <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
              {p.description}
            </p>
            <ul className="mt-4 flex flex-wrap gap-2">
              {p.tags.map((t) => (
                <li
                  key={t}
                  className="text-xs px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-900"
                >
                  {t}
                </li>
              ))}
            </ul>
          </a>
        ))}
      </div>
    </section>
  );
}
