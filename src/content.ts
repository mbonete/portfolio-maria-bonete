// The site's content. Every line comes from the project repos, the CV or PRODUCT.md; nothing here is
// invented. Copy follows the writing rules in CLAUDE.md.

export const person = {
  name: "Maria Bonete",
  email: "mbonetedev@gmail.com", // the one on the CV
  links: {
    github: "https://github.com/mbonete",
    linkedin: "https://www.linkedin.com/in/maria-bonete",
    cv: "/cv.pdf",
    siteRepo: "https://github.com/mbonete/portfolio-maria-bonete", // this site's code, public
  },
};

export type CaseStudy = {
  slug: "quote-and-nod" | "doorplate";
  title: string;
  summary: string;
  problem: string;
  stack: string[];
  built: string[];
  decisions: { title: string; body: string }[];
  model: string;
  repo?: string; // Left out for private repos: a link only a logged-in owner can open is a dead link.
  live?: string;
  videoId: string;
  videoLength: number; // seconds, for the play button's spoken label
  // Its colour on the site and the screens it shows: the desktop in a browser, and a phone in front.
  band: {
    ground: string;
    tone: "light" | "dark";
    desktop: { src: string; w: number; h: number; alt: string };
    phone?: { src: string; w: number; h: number; alt: string } | { loop: string; poster: string; label: string };
  };
};

export const caseStudies: CaseStudy[] = [
  {
    slug: "quote-and-nod",
    title: "Quote & Nod",
    summary:
      "A maintenance quote approval portal for property managers. The owner gets every vendor quote in one link and answers from their phone, and the decision stays on the job's record.",
    problem:
      "Quote & Nod covers one thing: a maintenance job, its vendor quotes, the owner's decision and the paper trail behind it. Rent collection, leases and tenant screening are left out on purpose.",
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
    videoLength: 24,
    band: {
      ground: "#b4492c",
      tone: "dark",
      desktop: {
        src: "/screens/qn-desktop.webp",
        w: 1600,
        h: 1000,
        alt: "The manager's job page: a water heater replacement with two vendor quotes, one recommended, waiting for the owner, Alice Chen.",
      },
      phone: {
        loop: "/screens/qn-loop.mp4",
        poster: "/screens/qn-loop.webp",
        label:
          "The owner's approval page on a phone: the two quotes, a message to the manager, then Approve and the confirmation.",
      },
    },
  },
  {
    slug: "doorplate",
    title: "Doorplate",
    summary:
      "Long-term rentals in Spain, listed by the people who own them. Each listing leads with its rent, rooms and floor area, and renters write to the owner from the listing page.",
    problem:
      "Doorplate covers one kind of rental: flats and houses let long term by their owners, priced in euros and measured in m². Holiday lets, sales and agency listings are left out. It started as Homely, a listings app whose ads had only a title, a description and photos; I renamed it and added the rental facts, search, enquiries and saved flats.",
    stack: ["Next.js (App Router)", "Server Components + Server Actions", "SQLite (better-sqlite3)", "Drizzle ORM", "Auth.js", "Zod", "Tailwind", "shadcn/ui"],
    built: [
      "Search by city, maximum rent, minimum bedrooms and floor area, sorted by newest, rent or size.",
      "Listing pages with the rent, bedrooms, bathrooms and floor area above the description, a photo grid and a viewer for every photo.",
      "An enquiry form (name, email, move-in date, message) that needs no account, and a page per listing where the owner reads the enquiries and replies by email.",
      "Saved flats for signed-in users, and sharing through the phone's share sheet or a copied link on desktop.",
      "Create, edit and delete flows for listings with several ordered photos.",
      "Sign-up and login with bcrypt-hashed passwords and a JWT session cookie; logging in returns you to the page you were on.",
      "A seed script with eight listings in four cities, Unsplash photos and a demo owner.",
    ],
    decisions: [
      {
        title: "Searches live in the URL",
        body: "The filters are a GET form, and the listings page reads them from the search params on the server. A search can be bookmarked or shared, and it works before any JavaScript loads.",
      },
      {
        title: "Ownership checked on the server",
        body: "Editing or deleting a listing checks that it belongs to the signed-in user, the enquiries page sends anyone but the owner back to the listing, and owners can't send an enquiry to their own flat. Zod validates every form on the server, and a form that fails keeps what was typed.",
      },
      {
        title: "Uploads outside public/",
        body: "Next.js only serves files that were in public/ at build time, so photos uploaded to a production build came back as 404s. They now live in data/uploads next to the database, behind a route handler that checks the file name, and still go through next/image.",
      },
      {
        title: "One server with a disk",
        body: "SQLite and photos on local disk keep the app to one process with no outside services. The cost is hosting: it needs a VPS or a container with a volume, so serverless platforms are out.",
      },
    ],
    model:
      "Users, listings (rent in whole euros, city, neighbourhood, flat or house, bedrooms, bathrooms and m²), photos ordered by position, enquiries and saved flats. A saved flat is keyed on the user and the listing, so it can only be saved once. Deleting a listing removes its photos, enquiries and saves by cascade. City and rent are indexed, and schema changes ship as SQL migrations.",
    repo: "https://github.com/mbonete/doorplate",
    videoId: "970LQDqIdUQ",
    videoLength: 30,
    band: {
      ground: "#1f6b4c",
      tone: "dark",
      desktop: {
        src: "/screens/doorplate-desktop.webp",
        w: 1600,
        h: 1000,
        alt: "A listing for a two-bedroom flat in Ruzafa, Valencia: its photos, €1,150 a month, 2 bedrooms, 1 bathroom, 78 m², and the form to write to the owner, Lucía Ferrer.",
      },
      phone: {
        loop: "/screens/doorplate-loop.mp4",
        poster: "/screens/doorplate-loop.webp",
        label:
          "A renter on a phone: the Ruzafa flat from the Valencia results, then a name and email in the form to Lucía, Send, and the confirmation.",
      },
    },
  },
];

export const marineWobbles = {
  title: "Marine Wobbles",
  status: "In internal testing on Google Play",
  summary:
    "A tap-to-pop match-3 for Android, written natively in Kotlin and Jetpack Compose, with a coin store that takes real payments through Google Play.",
  facts: [
    { k: "Levels", v: "80, in eight chapters; each chapter adds a new mechanic" },
    { k: "Difficulty", v: "Pacing follows flow theory and cognitive load research: one new rule at a time, difficulty rising with skill" },
    { k: "Balance", v: "7 strategy bots play every level; about 2.2 million seeded games per run" },
    { k: "Tests", v: "455 unit tests" },
    { k: "Art", v: "27 illustrated episodes, generated from my prompts" },
  ],
  stack: ["Kotlin", "Jetpack Compose", "Coroutines + StateFlow", "Play Billing", "kotlinx-serialization", "JUnit"],
  trailerId: "agdXKgTLqxc",
  trailerLength: 31, // seconds
};

// Open source: a panel for the cmux terminal and the local web dashboard that goes with it. Both repos
// are public under the MIT license. The screenshots show made-up sessions.
export const switchboard = {
  slug: "switchboard",
  title: "Switchboard",
  status: "Open source under the MIT license",
  summary:
    "A panel for the cmux terminal that sorts the coding agents I have running into four lists: waiting on me, working, finished, and gone stale. Tapping a row opens that agent's terminal.",
  stack: ["JavaScript", "cmux sidebar runtime", "Node.js", "Server-Sent Events"],
  panelRepo: "https://github.com/mbonete/cmux-switchboard-panel",
  dashboardRepo: "https://github.com/mbonete/cmux-switchboard",
  install: [
    "mkdir -p ~/.config/cmux/sidebars && \\",
    "curl -fsSL -o ~/.config/cmux/sidebars/switchboard.js \\",
    "  https://raw.githubusercontent.com/mbonete/cmux-switchboard-panel/main/switchboard.js && \\",
    "cmux right-sidebar set custom switchboard",
  ].join("\n"),
  lists: [
    { title: "Needs you", body: "An agent waiting for an answer or an approval, or a result I haven't read. The longest wait comes first." },
    { title: "Working", body: "Agents in the middle of a turn, with a live timer, my last prompt and how many subagents are running." },
    { title: "Your move", body: "Agents that finished and are waiting for my next message." },
    { title: "Stale", body: "No activity for longer than a threshold I pick: a day, two days or a week. Collapsed until I open it." },
  ],
  decisions: [
    {
      title: "The panel needs no server",
      body: "It reads the list of agents cmux already keeps, so nothing has to run alongside it. I've tested it with Claude Code.",
    },
    {
      title: "A reply only goes into an empty prompt",
      body: "The dashboard types a reply into the agent's terminal and presses Enter. Just before that, the server checks again that the agent is idle and its prompt box is empty, so a reply can't land in the middle of a turn or mix with a half-written draft.",
    },
    {
      title: "Answers go through cmux",
      body: "Allowing a command or answering a question uses cmux's Feed, which holds the agent's request for about two minutes before the agent falls back to its own prompt. The card counts that window down, then says to answer in the terminal.",
    },
    {
      title: "Stale counts from the last prompt",
      body: "cmux re-stamps an agent's last-activity time whenever it restores sessions after a restart, so Switchboard counts from the last prompt and the transcript, which a restart leaves alone.",
    },
    {
      title: "The dashboard stays on the machine",
      body: "It listens on 127.0.0.1, refuses requests addressed to any other host name, and every action needs a token created at start-up that only the page has, so another website open in the browser can't trigger one.",
    },
  ],
  band: {
    ground: "#f0a93b",
    tone: "light" as const,
    desktop: {
      src: "/screens/switchboard-desktop.webp",
      w: 1600,
      h: 1000,
      alt: "Switchboard's web dashboard: an agent asking to run the rate-limit tests, with Allow once, Always allow and Deny; an agent asking whether the second email goes out on day 3 or day 5; and two agents working, with their timers.",
    },
    panel: {
      src: "/screens/switchboard-panel.webp",
      w: 580,
      h: 1500,
      alt: "The Switchboard panel in cmux: two agents that need me, two working with live timers, two finished, and three stale ones collapsed.",
    },
  },
};

export const entries = [
  {
    title: "Guess The BPM",
    summary: "Tap along to a song and guess its tempo; within one beat per minute counts. YouTube playback, English and Spanish.",
    stack: ["React", "TypeScript", "Vite", "Tailwind", "i18next"],
    live: "https://guessthebpm.netlify.app",
    repo: "https://github.com/mbonete/guess-the-bpm",
  },
  {
    title: "The Coffee Place",
    summary:
      "A fictional café whose menu is a numbered series of six sugar sachets: tear one open into its page, stamp drinks into the cart and pay to a printed receipt.",
    stack: ["Next.js", "React", "JavaScript", "styled-components"],
    live: "https://the-coffee-place.vercel.app/",
    repo: "https://github.com/mbonete/coffee-place",
  },
];

// How I work with coding agents; an example only where it can be checked.
export const aiIntro = "I work with coding agents in Claude Code and Codex.";

export const aiPractices: { title: string; text: string; example?: string; link?: { lead: string; label: string; href: string } }[] = [
  {
    title: "Grilling to a shared understanding",
    text: "Before an agent writes any code, I have it grill me on the task until we understand it the same way. That's where the gaps come out: the case I hadn't mentioned, the assumption it would otherwise have made without asking.",
    example: "This portfolio was planned that way.",
  },
  {
    title: "Goals that end on evidence",
    text: "With Claude Code's /goal command, an agent keeps working until a separate model decides the goal is met, and that model only sees the conversation. So a good goal describes the finished state, names the commands that prove it, says what must not change, and sets a limit, such as 20 turns.",
  },
  {
    title: "The right model and effort for each task",
    text: "The strongest model at maximum effort is slower and costs more, and on routine work it rarely does better. Knowing which tasks need it is part of the job, and I revisit that choice whenever a new model comes out.",
  },
  {
    title: "Running agents in parallel",
    text: "Several agents working at once can get far more done in a day, as long as their tasks are independent and each has its own copy of the code. The real limit is review: once finished work starts waiting on me, another agent stops helping.",
    link: { lead: "To notice that sooner, I built", label: "Switchboard", href: "/work/switchboard" },
  },
  {
    title: "A different agent reviews the code",
    text: "Models tend to judge their own output too kindly, so the agent that wrote the code never reviews it. The review comes from a fresh session, and I check its findings before acting on them.",
  },
];

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
