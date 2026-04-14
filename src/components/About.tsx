const skillGroups: { title: string; items: string[] }[] = [
  {
    title: "Front-end",
    items: [
      "React",
      "JavaScript",
      "TypeScript",
      "Next.js",
      "Remix",
      "React Native",
      "Redux",
      "HTML",
      "NativeWind",
      "React Query",
      "SWR",
      "React Hook Form",
      "CSS",
      "Tailwind",
      "Styled Components",
    ],
  },
  {
    title: "Back-end",
    items: ["Node.js", "Express", "SQL", "Prisma", "Python"],
  },
  {
    title: "Web3",
    items: ["Metamask", "Wagmi", "Rainbowkit", "SIWE"],
  },
  {
    title: "Tooling",
    items: ["GitHub", "Git", "Jest", "Figma", "OAuth", "Photoshop", "Illustrator"],
  },
];

export default function About() {
  return (
    <section id="about" className="py-20 border-t border-neutral-200 dark:border-neutral-800">
      <h2 className="text-2xl font-semibold tracking-tight mb-6 flex items-center gap-3">
        <span aria-hidden className="inline-block h-5 w-1.5 rounded-sm bg-primary" />
        About
      </h2>
      <p className="max-w-2xl text-neutral-600 dark:text-neutral-400 leading-relaxed mb-10">
        I&apos;m a frontend developer based in Spain, focused on building
        thoughtful interfaces, design systems, and full-stack features across
        web and mobile. I care about performance, accessibility, and the small
        details that make products feel polished.
      </p>
      <div className="grid sm:grid-cols-2 gap-8">
        {skillGroups.map((group) => (
          <div key={group.title}>
            <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-widest mb-3">
              {group.title}
            </h3>
            <ul className="flex flex-wrap gap-2">
              {group.items.map((s) => (
                <li
                  key={s}
                  className="text-xs px-2.5 py-1 rounded-full border border-neutral-300 dark:border-neutral-700"
                >
                  {s}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
