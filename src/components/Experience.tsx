type Role = {
  company: string;
  title: string;
  period: string;
  summary: string;
  stack: string[];
};

const roles: Role[] = [
  {
    company: "Wandity",
    title: "Full Stack Developer",
    period: "Sept 2024 — Present",
    summary:
      "Leading architecture and development for an e-commerce platform's web and mobile apps. Built a new full-stack Next.js app in a monorepo with SQLite and Drizzle, and an offline-first React Native (Expo) app for the internal sales teams, with sync, SQLite storage and image caching. Also shipped an events and social app: React Native with a tRPC backend on Cloudflare Workers (Hono, D1).",
    stack: [
      "Next.js",
      "React Native (Expo)",
      "TypeScript",
      "tRPC",
      "Drizzle ORM",
      "SQLite",
      "React Query",
      "Zod",
      "NativeWind",
      "Sentry",
    ],
  },
  {
    company: "Bidz Labs",
    title: "Front-end Architect",
    period: "Mar 2024 — Sept 2024",
    summary:
      "Designed and built the front end of a Web3 trading and betting platform on my own: Ethereum smart contracts behind a hook-based SDK I wrote, real-time multi-token trading data over WebSockets, and sign-in with Ethereum (SIWE) or OAuth.",
    stack: [
      "React",
      "TypeScript",
      "Redux Toolkit",
      "React Query",
      "Wagmi",
      "RainbowKit",
      "WebSockets",
    ],
  },
  {
    company: "Aventu",
    title: "Freelance Front-end Developer",
    period: "Sept 2023 — Mar 2024",
    summary:
      "Delivered two fixed-price features for a story-creation app: a diagram-based story builder and an audio editor. Turned Figma designs into components and integrated REST APIs.",
    stack: ["React", "TypeScript", "React Flow", "Redux Toolkit", "RTK Query"],
  },
  {
    company: "CaneLab Ltd.",
    title: "Front-end Developer",
    period: "Aug 2022 — Dec 2023",
    summary:
      "Built interfaces for a consultancy that made custom products for startups and small businesses: designed screens in Figma, built them as components and integrated REST APIs.",
    stack: ["React", "Next.js", "TypeScript", "Styled Components", "Figma"],
  },
];

export default function Experience() {
  return (
    <section
      id="experience"
      className="md:py-20 py-16 border-t border-neutral-800"
    >
      <h2 className="text-2xl font-semibold tracking-tight mb-8 flex items-center gap-3">
        <span
          aria-hidden
          className="inline-block h-8 w-1.5 rounded-sm bg-primary"
        />
        Experience
      </h2>
      <ol className="relative border-l border-neutral-800 ml-2 space-y-10">
        {roles.map((role) => (
          <li key={`${role.company}-${role.period}`} className="pl-6 relative">
            <span
              aria-hidden
              className="absolute -left-1.25 top-2 h-2.5 w-2.5 rounded-full bg-primary shadow-[0_0_20px_var(--color-primary)]"
            />
            <div className="flex flex-wrap items-baseline justify-between gap-x-4">
              <h3 className="font-medium">
                {role.title}{" "}
                <span className="text-neutral-400">· {role.company}</span>
              </h3>
              <span className="text-xs uppercase tracking-widest text-neutral-400">
                {role.period}
              </span>
            </div>
            <p className="mt-2 text-sm text-neutral-400 leading-relaxed">
              {role.summary}
            </p>
            <ul className="mt-3 flex flex-wrap gap-2">
              {role.stack.map((s) => (
                <li
                  key={s}
                  className="text-xs px-2 py-0.5 rounded-full bg-neutral-900 text-neutral-400"
                >
                  {s}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ol>
    </section>
  );
}
