// Shared real content for the /lab POCs. Throwaway: the final rebuild owns its own data.

export const person = {
  name: "Maria Bonete",
  role: "Full-stack developer",
  specialties: ["React Native", "Web3", "AI-driven engineering"],
  tagline:
    "Full-stack developer, specialising in React Native, Web3 and AI-driven engineering.",
  location: "Spain",
  timezone: "Europe/Madrid",
  photo: "/lab/maria.png",
  cutout: "/lab/maria-cutout.png",
  links: {
    github: "https://github.com/mbonete",
    linkedin: "https://www.linkedin.com/in/maria-bonete",
    cv: "/cv.pdf",
  },
};

export const currently = {
  role: "Full Stack Developer at Wandity",
  company: "Wandity",
  building: "Agent-driven workflows for shipping production apps",
};

export type Project = {
  slug: string;
  title: string;
  kind: "case-study" | "entry";
  summary: string;
  tags: string[];
  href: string;
  image: string;
  videoId?: string;
};

export const projects: Project[] = [
  {
    slug: "dwelltrace",
    title: "Dwelltrace",
    kind: "case-study",
    summary:
      "A lightweight maintenance quote approval portal for small property managers: vendor quotes, owner approvals and job tracking in one workflow.",
    tags: ["Next.js", "TypeScript", "Tailwind", "Supabase", "Drizzle"],
    href: "https://www.youtube.com/watch?v=VIHxOCpGPLg",
    image: "/dwelltrace-poster.webp",
    videoId: "VIHxOCpGPLg",
  },
  {
    slug: "homely",
    title: "Homely",
    kind: "case-study",
    summary:
      "A full-stack real estate listings app with authentication, image uploads, and a SQLite-backed CRUD flow.",
    tags: ["Next.js", "Tailwind", "shadcn/ui", "Drizzle", "Auth.js"],
    href: "https://github.com/mbonete/homely",
    image: "/homely-poster.webp",
    videoId: "Ygp6AJwHytE",
  },
  {
    slug: "guess-the-bpm",
    title: "Guess The BPM",
    kind: "entry",
    summary:
      "Tap along to a song for fifteen seconds and guess its tempo; within one beat per minute counts. YouTube playback, English and Spanish.",
    tags: ["React", "TypeScript", "Vite", "Tailwind", "i18n"],
    href: "https://guessthebpm.netlify.app",
    image: "/guessthebpm.webp",
  },
  {
    slug: "the-coffee-place",
    title: "The Coffee Place",
    kind: "entry",
    summary:
      "A fictional café whose menu is a numbered series of six sugar sachets: tear one open into its page, stamp drinks into the cart and pay to a printed receipt.",
    tags: ["Next.js", "JavaScript", "Styled Components"],
    href: "https://the-coffee-place.vercel.app/",
    image: "/the-coffee-place.webp",
  },
];

export const sections = [
  { id: "projects", label: "Projects" },
  { id: "ai", label: "AI" },
  { id: "experience", label: "Experience" },
  { id: "about", label: "About" },
  { id: "contact", label: "Contact" },
];
