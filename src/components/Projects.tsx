import Image from "next/image";

type Project = {
  title: string;
  description: string;
  tags: string[];
  href: string;
  preview?: string;
  video?: string;
};

const projects: Project[] = [
  {
    title: "The Coffee Place",
    description:
      "Showcases the artistry of a fictional coffee shop, letting users explore offerings and place orders.",
    tags: ["Next.js", "JavaScript", "Styled Components"],
    href: "https://the-coffee-place.vercel.app/",
    preview: "/coffee-place.svg",
  },
  {
    title: "Mago del Regalo",
    description:
      "AI-powered app that eliminates the challenge of finding gift ideas.",
    tags: ["Next.js", "TypeScript", "MaterialUI", "React Query"],
    href: "https://www.magodelregalo.com",
    preview: "/magodelregalo.svg",
  },
  {
    title: "Guess The BPM",
    description:
      "A web-based game where users guess the beats per minute of a song. YouTube API integration with i18n support.",
    tags: ["React", "Styled Components"],
    href: "https://www.guess-the-bpm.com",
    preview: "/guessthebpm.svg",
  },
  {
    title: "Homely",
    description:
      "A minimal real estate platform built as a proof of concept for integration with a CRUD API.",
    tags: ["React", "React Hook Form", "React Query", "MaterialUI"],
    href: "https://github.com/mbonete/homely",
    video: "https://www.youtube.com/embed/lGpt8-h8XWY",
  },
];

export default function Projects() {
  return (
    <section id="projects" className="py-20 border-t border-neutral-800">
      <h2 className="text-2xl font-semibold tracking-tight mb-6 flex items-center gap-3">
        <span
          aria-hidden
          className="inline-block h-8 w-1.5 rounded-sm bg-primary"
        />
        Projects
      </h2>
      <div className="grid sm:grid-cols-2 gap-5">
        {projects.map((project) => (
          <a
            key={project.title}
            href={project.href}
            target="_blank"
            rel="noreferrer"
            className="group flex flex-col justify-between rounded-xl border border-neutral-800 p-5 bg-background/40 backdrop-blur-sm hover:border-primary/60 hover:shadow-[0_0_30px_-10px_var(--color-primary)] transition"
          >
            <div>
              <h3 className="font-medium group-hover:translate-x-0.5 transition-transform">
                {project.title}
              </h3>
              <p className="mt-2 text-sm text-neutral-400">
                {project.description}
              </p>
            </div>
            {project.preview && (
              <div className="overflow-hidden rounded-xl my-4">
                <Image
                  src={project.preview}
                  alt={`${project.title} preview`}
                  width={800}
                  height={450}
                  unoptimized
                  loading="eager"
                  className="w-full h-auto"
                />
              </div>
            )}
            {project.video && (
              <div className="relative aspect-video overflow-hidden rounded-xl my-4">
                <iframe
                  src={project.video}
                  title={`${project.title} video`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="absolute inset-0 h-full w-full"
                />
              </div>
            )}
            <ul className="mt-4 flex flex-wrap gap-2">
              {project.tags.map((tag) => (
                <li
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full bg-neutral-800"
                >
                  {tag}
                </li>
              ))}
            </ul>
          </a>
        ))}
      </div>
    </section>
  );
}
