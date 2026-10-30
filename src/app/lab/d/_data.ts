// Proof shown when an area is pulled into the hero frame. Facts only: every line
// comes from the CV, the project repos, or measured results described generically.

export type AreaId = "fullstack" | "mobile" | "web3" | "ai";

export type Proof = { title: string; fact: string; href?: string };

export type Area = {
  id: AreaId;
  label: string;
  giant: string;
  proof: Proof[];
};

export const areas: Area[] = [
  {
    id: "fullstack",
    label: "Full-stack",
    giant: "FULLSTACK",
    proof: [
      {
        title: "Dwelltrace",
        fact: "Quote approvals for property managers. Next.js, Supabase, Drizzle.",
        href: "https://github.com/mbonete/dwelltrace",
      },
      {
        title: "Homely",
        fact: "Listings with auth, uploads and a SQLite-backed CRUD flow.",
        href: "https://github.com/mbonete/homely",
      },
      {
        title: "Wandity",
        fact: "Greenfield Next.js web app on a monorepo with SQLite and Drizzle.",
      },
    ],
  },
  {
    id: "mobile",
    label: "Mobile",
    giant: "MOBILE",
    proof: [
      {
        title: "Marine Wobbles",
        fact: "Native Android game in Kotlin and Jetpack Compose. In development.",
        href: "#marine-wobbles",
      },
      {
        title: "Wandity sales app",
        fact: "Offline-first React Native (Expo) app with sync and SQLite storage.",
      },
      {
        title: "Wandity events app",
        fact: "React Native and tRPC on Cloudflare Workers (Hono, D1).",
      },
    ],
  },
  {
    id: "web3",
    label: "Web3",
    giant: "WEB3",
    proof: [
      {
        title: "Bidz Labs",
        fact: "Front-end architect for a Web3 trading and betting platform.",
      },
      {
        title: "Contracts and SDK",
        fact: "Ethereum contract integration and a hook-based SDK.",
      },
      {
        title: "Real-time and auth",
        fact: "Multi-token data over WebSockets; SIWE and OAuth sign-in.",
      },
    ],
  },
  {
    id: "ai",
    label: "AI-driven engineering",
    giant: "AI",
    proof: [
      {
        title: "Outcomes, not step lists",
        fact: "Controlled A/B: both scored 6/6; the step-list run was ~8× slower on large inputs.",
      },
      {
        title: "Green checks are proxies",
        fact: "A $1.86 autonomous run passed every check; real input rejected it; fixed for $0.41.",
      },
      {
        title: "Effort is a budget",
        fact: "High effort cost 2.2× and took 2.9× longer for the same 9/9 result.",
      },
    ],
  },
];
