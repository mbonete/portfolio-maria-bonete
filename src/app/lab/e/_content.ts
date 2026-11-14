// Content for POC E below the hero. Every line comes from the project repos, the CV, PRODUCT.md or
// measured results described generically; nothing here is invented.

export type CaseStudy = {
  slug: "quote-and-nod" | "homely";
  title: string;
  summary: string;
  problem: string;
  image: { src: string; w: number; h: number; alt: string };
  stack: string[];
  built: string[];
  decisions: { title: string; body: string }[];
  model: string;
  repo?: string; // Left out for private repos: a link only a logged-in owner can open is a dead link.
  live?: string;
  videoId: string;
};

export const caseStudies: CaseStudy[] = [
  {
    slug: "quote-and-nod",
    title: "Quote & Nod",
    summary:
      "A maintenance quote approval portal for property managers. The owner gets every vendor quote in one link and answers from their phone, and the decision stays on the job's record.",
    problem:
      "Quote & Nod covers one thing: a maintenance job, its vendor quotes, the owner's decision and the paper trail behind it. Rent collection, leases and tenant screening are left out on purpose.",
    image: { src: "/quote-and-nod-poster.webp", w: 800, h: 450, alt: "Quote & Nod: a water heater job with two vendor quotes, and the owner's approval page on a phone." },
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
    videoId: "Qil40vL6FCY",
  },
  {
    slug: "homely",
    title: "Homely",
    summary:
      "A full-stack real estate listings app with accounts, photo uploads and a SQLite database.",
    problem:
      "Browse homes, open a listing, and sign in to post and manage your own ads with photos. It's built around the App Router's server model.",
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
  status: "In internal testing on Google Play",
  summary:
    "A tap-to-pop match-3 for Android, written natively in Kotlin and Jetpack Compose, with a coin store that takes real payments through Google Play.",
  facts: [
    { k: "Levels", v: "80, in eight chapters; each chapter adds a new mechanic" },
    { k: "Difficulty", v: "7 strategy bots; about 2.2 million seeded games per balance run" },
    { k: "Tests", v: "455 unit tests, and 264 recorded games replayed state for state" },
    { k: "Art", v: "27 illustrated episodes, generated from my prompts" },
  ],
  highlights: [
    {
      title: "Bots measure every level",
      body: "The strategy bots run the game's real rule code, 2,000 to 5,000 seeded games each per level. Each difficulty tier sets limits: a win-rate band, when in the move budget a win should land, and how far skilled play must beat random play. Tests hold every level to its tier, and an auto-tuner proposes fixes.",
    },
    {
      title: "A port that replays exactly",
      body: "The rules are a port of my TypeScript prototype, random generator included, bit for bit. Games recorded in the prototype replay identically in Kotlin, and the prototype's win-rate table comes out identical.",
    },
    {
      title: "Purchases that can't be lost or doubled",
      body: "Coins are granted once a purchase completes and saved before the purchase is consumed. The purchase token is the key, so nothing is granted twice, and unfinished purchases are re-checked whenever the game comes back. Tested with approved, declined, cancelled and slow payments.",
    },
  ],
  stack: ["Kotlin", "Jetpack Compose", "Coroutines + StateFlow", "Play Billing", "kotlinx-serialization", "JUnit"],
  trailerId: "agdXKgTLqxc",
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
    summary:
      "A fictional café whose menu is a numbered series of six sugar sachets: tear one open into its page, stamp drinks into the cart and pay to a printed receipt.",
    stack: ["Next.js", "React", "JavaScript", "styled-components"],
    image: { src: "/the-coffee-place.webp", w: 2880, h: 1800 },
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
  { id: "marine-wobbles", label: "Marine Wobbles", hint: "In testing", keywords: "kotlin android game", href: "#marine-wobbles" },
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

// How I work with coding agents, in the order of a piece of work; an example only where it can be checked.
export const aiPractices: { title: string; text: string; example?: string }[] = [
  {
    title: "Grilling to a shared understanding",
    text: "Before an agent writes any code, I have it grill me on the task until we understand it the same way. That's where the gaps come out: the case I hadn't mentioned, the assumption it would otherwise have made without asking.",
    example: "This portfolio was planned that way.",
  },
  {
    title: "Goals that end on evidence",
    text: "With /goal, an agent keeps working until a separate model decides the goal is met, and that model only sees the conversation. So a good goal describes the finished state, names the commands that prove it, says what must not change, and sets a limit, such as 20 turns.",
  },
  {
    title: "The right model and effort for each task",
    text: "The strongest model at maximum effort is slower and costs more, and on routine work it rarely does better. Knowing which tasks need it is part of the job, and I revisit that choice whenever a new model comes out.",
  },
  {
    title: "Running agents in parallel",
    text: "Several agents working at once can get far more done in a day, as long as their tasks are independent and each has its own copy of the code. The real limit is review: once finished work starts waiting on me, another agent stops helping.",
  },
  {
    title: "A different agent reviews the code",
    text: "Models tend to judge their own output too kindly, so the agent that wrote the code never reviews it. The review comes from a fresh session, and I check its findings before acting on them.",
  },
];

export const ai = {
  principles: [
    {
      title: "I watch a new test fail before I trust it.",
      body: "I plant the defect a new test guards and confirm the unchanged test catches it.",
    },
    {
      title: "The agent that writes the code doesn't verify it.",
      body: "Review comes from a fresh session, ideally another model family, and the reviewer gets checked too.",
    },
    {
      title: "I describe the outcome and leave the steps to the agent.",
      body: "Agents get the goal, constraints and acceptance checks, not a script.",
    },
    {
      title: "Work is done when it handles real input.",
      body: "Work is accepted after it meets real inputs and my own judgment, because taste is still my job.",
    },
    {
      title: "I measure what extra effort buys.",
      body: "Effort, parallelism and process are tuned per accepted result, not maxed out.",
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
      "Built interfaces for a consultancy making custom products for startups and small businesses, from Figma designs to components, with REST integrations.",
    ],
    stack: "React · Next.js · TypeScript · styled-components · Figma",
  },
];
