import Image from "next/image";
import LiteYouTube from "./LiteYouTube";

type Project = {
  title: string;
  description: string;
  tags: string[];
  href: string;
  preview?: string;
  videoId?: string;
  poster?: string;
};

const projects: Project[] = [
  {
    title: "Quote & Nod",
    description:
      "A maintenance quote approval portal for property managers. The owner gets every vendor quote in one link and answers from their phone, and the decision stays on the job's record.",
    tags: ["Next.js", "TypeScript", "Tailwind", "Supabase", "Drizzle"],
    href: "https://www.youtube.com/watch?v=Qil40vL6FCY",
    videoId: "Qil40vL6FCY",
    poster: "/quote-and-nod-poster.webp",
  },
  {
    title: "Homely",
    description:
      "A full-stack real estate listings app with accounts, photo uploads and a SQLite database.",
    tags: ["Next.js", "Tailwind", "shadcn/ui", "Drizzle", "Auth.js"],
    href: "https://github.com/mbonete/homely",
    videoId: "Ygp6AJwHytE",
    poster: "/homely-poster.webp",
  },
  {
    title: "Guess The BPM",
    description:
      "Tap along to a song for fifteen seconds and guess its tempo; within one beat per minute counts. YouTube playback, English and Spanish.",
    tags: ["React", "TypeScript", "Vite", "Tailwind", "i18n"],
    href: "https://guessthebpm.netlify.app",
    preview: "/guessthebpm.webp",
  },
  {
    title: "The Coffee Place",
    description:
      "A fictional café whose menu is a numbered series of six sugar sachets: tear one open into its page, stamp drinks into the cart and pay to a printed receipt.",
    tags: ["Next.js", "JavaScript", "Styled Components"],
    href: "https://the-coffee-place.vercel.app/",
    preview: "/the-coffee-place.webp",
  },
];

export default function Projects() {
  return (
    <section
      id="projects"
      className="md:py-20 py-16 border-t border-neutral-800"
    >
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
                  sizes="(min-width: 1024px) 580px, (min-width: 640px) 50vw, 100vw"
                  quality={70}
                  className="w-full h-auto"
                />
              </div>
            )}
            {project.videoId && (
              <LiteYouTube
                videoId={project.videoId}
                title={`${project.title} demo`}
                poster={project.poster}
              />
            )}
            <ul className="mt-4 flex flex-wrap gap-2">
              {project.tags.map((tag) => (
                <li
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full bg-neutral-900"
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
