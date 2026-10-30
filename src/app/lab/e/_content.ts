// Content for POC E below the hero. Every line comes from the project repos, the CV, PRODUCT.md or
// measured results described generically; nothing here is invented.

export type CaseStudy = {
  slug: "dwelltrace" | "homely";
  title: string;
  summary: string;
  problem: string;
  image: { src: string; w: number; h: number; alt: string };
  stack: string[];
  built: string[];
  decisions: { title: string; body: string }[];
  model: string;
  repo?: string; // Left out for private repos: a link only a logged-in owner can open is a dead link.
  videoId: string;
};

export const caseStudies: CaseStudy[] = [
  {
    slug: "dwelltrace",
    title: "Dwelltrace",
    summary:
      "A lightweight maintenance quote approval portal for small property managers: vendor quotes, owner approvals and job tracking in one workflow.",
    problem:
      "Maintenance approvals, without the mess. Dwelltrace keeps a job, its vendor quotes, the owner's decision and the paper trail in one workflow, and deliberately stops there: no rent collection, no leases, no tenant screening.",
    image: { src: "/dwelltrace-poster.webp", w: 800, h: 450, alt: "Dwelltrace dashboard with maintenance jobs grouped into four buckets." },
    stack: ["Next.js (App Router)", "TypeScript", "Supabase (Postgres, Auth, Storage)", "Drizzle ORM", "React Hook Form + Zod", "Radix primitives", "Tailwind", "Resend"],
    built: [
      "Email and password auth with session refresh and route protection.",
      "Properties, with the owner's contact created or updated alongside.",
      "Jobs that move through eight statuses, from new to closed, with urgency, scheduling and completion.",
      "Quotes per job, with one marked as recommended for the owner.",
      "Attachments in private storage, served through short-lived signed links.",
      "Comments that can be internal or visible to the owner.",
      "A typed activity timeline for every job.",
      "A tokenized owner portal to approve, reject or ask a question.",
      "Emails for approval requests, confirmations, rejections and completion.",
      "A dashboard sorted into four buckets, and a seed script for demos.",
    ],
    decisions: [
      {
        title: "Owners don't need an account",
        body: "Owners approve through a link carrying a random 24-byte token with a 30-day expiry; sending it again rotates it. The trade-off against magic links is documented, with an upgrade path to an emailed one-time code.",
      },
      {
        title: "Authorization lives in every action",
        body: "Each server action verifies the session itself and re-checks that the row belongs to the manager, because route protection is not trusted to authorize.",
      },
      {
        title: "Locked down by default",
        body: "Row Level Security is on for every table with no policies, so the public API exposes nothing. Storage is private, uploads are capped at 10 MB, and every input is validated on the server.",
      },
      {
        title: "Runs locally end to end",
        body: "Without an email key the mailer logs instead of sending, and environment variables are validated at start-up, so the whole approval flow works on a laptop.",
      },
    ],
    model:
      "Users, owner contacts, properties, maintenance jobs, quotes (amounts in cents), attachments, comments and a typed event stream with JSON metadata. UUID keys, timestamps with time zones, and a unique index on the owner's access token.",
    videoId: "VIHxOCpGPLg",
  },
  {
    slug: "homely",
    title: "Homely",
    summary:
      "A full-stack real estate listings app with authentication, image uploads and a SQLite-backed CRUD flow.",
    problem:
      "A listings app built around the App Router's server model: browse homes, open a listing, and sign in to publish and manage your own ads with photos.",
    image: { src: "/lab/d/homely.webp", w: 1280, h: 686, alt: "Homely listings page with property cards." },
    stack: ["Next.js (App Router)", "Server Components + Server Actions", "SQLite (better-sqlite3)", "Drizzle ORM", "Auth.js", "Zod", "Tailwind", "shadcn/ui"],
    built: [
      "Landing page, listings index and listing detail.",
      "Create and edit flows for ads, with multiple ordered images.",
      "Sign-up and login with hashed passwords and an httpOnly session cookie.",
      "A profile page listing the user's own ads.",
    ],
    decisions: [
      {
        title: "Server-first data flow",
        body: "Pages read straight from the database in Server Components, with no client-side fetching. Every write is a Server Action with pending and error states handled in the form.",
      },
      {
        title: "Ownership on every write",
        body: "Editing or deleting an ad checks that it belongs to the signed-in user; inputs are validated with Zod and uploads get random UUID names.",
      },
      {
        title: "Protected routes",
        body: "Creating ads, editing them and user pages sit behind an auth proxy.",
      },
    ],
    model: "Users, ads and ad images ordered by position, with images removed when their ad is deleted. Schema changes ship as SQL migrations.",
    repo: "https://github.com/mbonete/homely",
    videoId: "Ygp6AJwHytE",
  },
];

export const marineWobbles = {
  title: "Marine Wobbles",
  status: "In development for Google Play",
  summary:
    "A tap-to-pop match-3 for Android, built natively in Kotlin and Jetpack Compose. Its difficulty is measured, not guessed: five strategy bots play thousands of seeded games to tune every level.",
  facts: [
    { k: "Levels", v: "80, in eight chapters that each add one mechanic" },
    { k: "Painted episodes", v: "27, each with a map, level card and victory scene" },
    { k: "Tuning", v: "Bot win rates from seeded simulations; only changed levels are re-measured" },
    { k: "Tests", v: "45 unit-test files over pure game rules" },
  ],
  stack: ["Kotlin", "Jetpack Compose", "kotlinx-serialization", "JUnit"],
};

export const entries = [
  {
    title: "Guess The BPM",
    summary: "Tap along to a song for fifteen seconds and guess its tempo; within one beat per minute counts. YouTube playback, English and Spanish.",
    stack: ["React", "TypeScript", "Vite", "Tailwind", "i18next"],
    image: { src: "/guessthebpm.webp", w: 800, h: 520 },
    live: "https://guessthebpm.netlify.app",
    repo: "https://github.com/mbonete/guess-the-bpm",
  },
  {
    title: "The Coffee Place",
    summary: "An editorial-brutalist shop for a fictional coffee roaster: explore the offerings and place an order.",
    stack: ["Next.js", "JavaScript", "styled-components"],
    image: { src: "/the-coffee-place.webp", w: 2760, h: 1766 },
    live: "https://the-coffee-place.vercel.app/",
    repo: "https://github.com/mbonete/coffee-place",
  },
];

// The command palette's rows here: the site's own words, and the site's own pages where they exist.
export const paletteSections = [
  { id: "projects", label: "Work" },
  { id: "ai", label: "AI" },
  { id: "experience", label: "Experience" },
  { id: "about", label: "About" },
  { id: "contact", label: "Contact" },
];

export const paletteWork = [
  { id: "marine-wobbles", label: "Marine Wobbles", hint: "In development", keywords: "kotlin android game", href: "#marine-wobbles" },
  ...caseStudies.map((c) => ({
    id: c.slug,
    label: c.title,
    hint: "Case study",
    keywords: c.stack.join(" "),
    href: `/lab/e/work/${c.slug}`,
  })),
  ...entries.map((e) => ({ id: e.title, label: e.title, hint: "Live site", keywords: e.stack.join(" "), href: e.live })),
  { id: "built", label: "How this site was built", hint: "Page", keywords: "agents process", href: "/lab/e/built" },
];

export const contactLine = "The quickest way to reach me is a message on LinkedIn.";

export const ai = {
  stance:
    "Agents make me faster only when I can show what they did. I give them outcomes and limits, measure what each result costs, and treat their output as a claim until real inputs and a second reviewer agree.",
  principles: [
    {
      title: "A test is unproven until I've seen it fail.",
      body: "I plant the defect a new test guards and confirm the unchanged test catches it.",
      result: "A planted logic bug passed every unit and browser test because no fixture covered it. The test that caught it became a reusable agent skill; in one autonomous run, 17 injected defects were each caught.",
    },
    {
      title: "The agent that writes the code doesn't verify it.",
      body: "Review comes from a fresh session, ideally another model family, and the reviewer gets checked too.",
      result: "A cross-provider reviewer found a real race condition; 5 of its 6 design concerns were accepted. It also once reviewed the wrong folder, which is why reviewers get reviewed.",
    },
    {
      title: "Outcomes, not step lists.",
      body: "Agents get the goal, constraints and acceptance checks, not a script.",
      result: "Controlled A/B: both briefs scored 6/6; the step-list run was about 8× slower on large inputs.",
    },
    {
      title: "Green checks are proxies.",
      body: "Work is accepted after it meets real inputs and my own judgment, because taste is still my job.",
      result: "An autonomous run passed every written check in 7 minutes; real input rejected it. A failing real-data check came first, then a fresh agent fixed the cause for under a quarter of the first run's cost.",
    },
    {
      title: "Effort is a budget I measure.",
      body: "Effort, parallelism and process are tuned per accepted result, not maxed out.",
      result: "Same model, low against high effort on held-out tests: both 9/9. High effort cost 2.2× and took 2.9× longer, buying readability, not correctness.",
    },
  ],
  toolkit: [
    { title: "Grilling", body: "The agent interviews me, recommends an answer to every question, and I decide. This site was designed that way.", tags: ["Claude Code", "skills"] },
    { title: "Bounded autonomous runs", body: "Outcome brief, hidden acceptance tests, budget and time limits, and knowing which limits the tool really enforces.", tags: ["/goal", "claude -p"] },
    { title: "Multi-agent workflows", body: "Parallel workers in isolated worktrees, a committed contract between them, an integrator, and recovery after a failed run.", tags: ["workflows", "git worktree"] },
    { title: "Adversarial review", body: "Several reviewers, then sceptical verifiers that confirm or reject each finding before anyone acts on it.", tags: ["ultracode"] },
    { title: "Cross-provider review", body: "One model family writes, another reviews, and the reviewer's claims are checked too.", tags: ["Claude Code", "Codex"] },
    { title: "Skills and project rules", body: "Tested for when they should and shouldn't trigger; rules kept to about 250 tokens; instructions that prevent nothing get removed.", tags: ["skills", "CLAUDE.md"] },
    { title: "Agent security", body: "Anything a tool reads is data, never instructions; least privilege; the actions that need a human are listed up front.", tags: ["permissions", "sandbox"] },
    { title: "Browser-in-the-loop checks", body: "The agent checks the real interface and network traffic, not only the tests. It caught an 18 px phone-only wrap that tests missed for three rounds.", tags: ["MCP", "Claude in Chrome"] },
  ],
};

export const experience = [
  {
    id: "wandity",
    company: "Wandity",
    role: "Full Stack Developer",
    dates: "Sept 2024 – now",
    points: [
      "Led architecture, design and front end for an e-commerce platform's web and mobile apps, including a greenfield Next.js app on a monorepo with shared packages, SQLite and Drizzle.",
      "Built an offline-first React Native (Expo) app for sales teams: orders created offline and synced later, SQLite storage, image caching, tuned for large catalogues on low-end devices.",
      "Owned the UI of a startup's events app: React Native with a tRPC backend on Cloudflare Workers (Hono, D1), schema and migrations, and dev, staging and production deploys.",
    ],
    stack: "Next.js · React Native · TypeScript · tRPC · Drizzle · SQLite · React Query · Zod · Sentry",
  },
  {
    id: "bidz-labs",
    company: "Bidz Labs",
    role: "Front-end Architect, Web3",
    dates: "Mar – Sept 2024",
    points: [
      "Designed and built the front end of a Web3 trading and betting app with social features, including wallet flows.",
      "Integrated Ethereum smart contracts behind a hook-based SDK; real-time multi-token data over WebSockets; sign-in with Ethereum and OAuth.",
      "Built trade creation, infinite feeds and trade modals, and wrote the internal architecture documentation.",
    ],
    stack: "React · TypeScript · Redux Toolkit · React Query · Wagmi · RainbowKit · WebSockets",
  },
  {
    id: "aventu",
    company: "Aventu",
    role: "Front-end Developer, freelance",
    dates: "Sept 2023 – Mar 2024",
    points: [
      "Delivered two fixed-price features for a story-creation app and was hired back for the second: a diagram-based story builder and an audio editor.",
    ],
    stack: "React · TypeScript · React Flow · Redux Toolkit · RTK Query",
  },
  {
    id: "canelab",
    company: "CaneLab Ltd.",
    role: "Front-end Developer",
    dates: "Aug 2022 – Dec 2023",
    points: [
      "Built interfaces for a consultancy making tailor-made products for startups and small businesses, from Figma designs to components, with REST integrations.",
    ],
    stack: "React · Next.js · TypeScript · styled-components · Figma",
  },
];
