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
    <section id="about" className="py-20 border-t border-neutral-800">
      <h2 className="text-2xl font-semibold tracking-tight mb-6 flex items-center gap-3">
        <span
          aria-hidden
          className="inline-block h-8 w-1.5 rounded-sm bg-primary"
        />
        About
      </h2>
      <div className="max-w-2xl text-neutral-400 leading-relaxed mb-10 space-y-4">
        <p>
          I&apos;m a full-stack developer specialized in building front-ends for
          web and mobile applications, with a recent focus on hybrid apps built
          on React Native and Expo. I&apos;ve shipped everything from
          offline-first e-commerce apps to Web3 trading platforms.
        </p>
        <p>
          My background is a little unusual — I studied Art History at
          Complutense University of Madrid before moving into development, which
          is where my eye for design and attention to detail come from. Native
          Spanish, advanced English (C1), and years of remote collaboration.
        </p>
      </div>
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
