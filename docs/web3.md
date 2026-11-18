# Web3 on the site

## Decision, 2026-11-18

Web3 is out of the hero, the meta description and the positioning in `PRODUCT.md`. The Work section has no Web3 project, so the claim rested on one role.

What stays: the Bidz Labs entry in Experience (Front-end Architect, Web3, Mar–Sept 2024) and the CV, both unchanged.

## When it comes back

When a Web3 project has its own section in Work, with a live site or a public repo.

## What that project could show

The Bidz Labs work, in a project that can be opened:

- Wallet connection with Wagmi and RainbowKit.
- Sign-in with Ethereum (SIWE).
- Reading from and writing to a contract on a testnet.
- Live token data over WebSockets.

## Putting it back

The wording to restore, matching the copy as it stands without Web3:

- `src/app/page.tsx`, hero on desktop and tablet (`.lf-role-wide`):
  "Web, mobile (React Native and native Android) and Web3, working with coding agents."
- `src/app/page.tsx`, hero on phones (`.lf-role-narrow`):
  "Web, React Native, native Android and Web3, working with coding agents."
- `src/app/layout.tsx`, meta description:
  "Full-stack developer working remotely from Madrid: web, mobile (React Native and native Android) and Web3. Case studies, shipped projects, and how I work with coding agents."
- `PRODUCT.md`:
  - Users: add Web3 to the roles.
  - Positioning: back to four areas ("full-stack web, mobile, Web3, and AI-driven engineering", AI "a peer of the other three"), and drop the sentence pointing here.
  - Product Principles 1: "four pillars".
- Work: the project's band in `bands` (`src/app/page.tsx`), which also adds it to the Work index, and its copy in `src/content.ts`.
- CV: the project under Side Projects.

Then check that the phone hero still fits the first screen at 360×640 and 390×664 (the phone line measured two lines with Web3 in it).
