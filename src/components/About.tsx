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
    items: [
      "GitHub",
      "Git",
      "Jest",
      "Figma",
      "OAuth",
      "Photoshop",
      "Illustrator",
    ],
  },
];

export default function About() {
  return (
    <section id="about" className="md:py-20 py-16 border-t border-neutral-800">
      <h2 className="text-2xl font-semibold tracking-tight mb-6 flex items-center gap-3">
        <span
          aria-hidden
          className="inline-block h-8 w-1.5 rounded-sm bg-primary"
        />
        About
      </h2>
      <div className="text-neutral-400 leading-relaxed mb-10 space-y-4">
        <p>
          I’m a motivated full-stack developer specialized in building
          front-ends for diverse web and mobile applications, with a recent
          focus on hybrid apps built on React Native. I have a proven ability to
          leverage a keen eye for design to implement intuitive solutions in
          accordance with best practices.
        </p>
        <p>
          As an effective communicator, I bring native Spanish and advanced
          English (CAE/C1) skills, along with significant experience in remote
          roles. My background also includes work on crypto and Web3 projects,
          and I’m currently seeking dynamic web development roles.
        </p>
      </div>
      <div className="grid sm:grid-cols-2 gap-8">
        {skillGroups.map((group) => (
          <div key={group.title}>
            <h3 className="text-sm font-medium text-neutral-400 uppercase tracking-widest mb-3">
              {group.title}
            </h3>
            <ul className="flex flex-wrap gap-2">
              {group.items.map((s) => (
                <li
                  key={s}
                  className="text-xs px-2.5 py-1 rounded-full border border-neutral-700"
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
