# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Recruiters and hiring managers filling full-stack, mobile (React Native / native Android) and AI-engineering roles. They often arrive from LinkedIn on a phone, between other candidates. Their first job is a ten-second decision: shortlist or move on. Their second job, once interested, is to check the proof: shipped work, roles, and how she works.

## Product Purpose

The personal portfolio of Maria Bonete, a developer based in Madrid, Spain, with a BA in Art History (Complutense University of Madrid, Extraordinary Award 9.48/10, Excellence Scholarship, 17 honours) who moved into software. It exists to get her shortlisted. Success is a visitor contacting her, downloading the CV, or opening LinkedIn/GitHub.

## Positioning

A developer who ships across three areas with equal weight: full-stack web, mobile (React Native and native Android), and AI-driven engineering. AI knowledge must be clear from the very first viewport, presented as a peer of the other two, not an add-on. Web3 is out of the positioning until a Web3 project is on the site; the Bidz Labs role keeps it in Experience and the CV (see `docs/web3.md`). Her AI angle is command of the tools: she gets better results and productivity from agents, and keeps her practice current as new models and tools are released. Shown through what she does, not stated as a claim.

## Operating Context

Visitors skim on phones and laptops, often in a recruiting pipeline with many tabs open. Deeper visitors (engineering managers) open case studies, the CV PDF, and GitHub repos.

## Capabilities and Constraints

- Next.js 16 (App Router), React 19, Tailwind 4; deployed as a static-friendly site.
- Routes: `/` (hero, work, "Engineering, now with agents", experience, contact), `/work/marine-wobbles`, `/work/quote-and-nod`, `/work/doorplate`, `/how-this-site-was-built`, `/blog` and one page per article (`/blog/<slug>`, text in `src/articles`; linked from nowhere on `/` for now, owner's call). All static.
- The site: a Blender-rendered gold folding screen on an azurite ground as the hero (folds shut at a click); one flat colour per project with its real product in a rendered phone frame and/or browser window; short silent loops in the phones; YouTube demos that play in place (privacy-enhanced, loaded on click).
- Mobile: LCP under 2.5s on a mid-range phone; heavy effects degrade on small screens and under reduced motion.
- Free fonts only.

## Brand Commitments

- Design reference, not content: her taste is Bosch's *The Garden of Earthly Delights* (her desktop wallpaper), Japanese and Chinese art, and Art Nouveau; her own work leans to glossy inflated 3D, flowing lines and purple. Her hobbies (photography, travel, art, books, music) inform the design but are not shown as site content.
- Do not mention job-seeking. Use only photos of Maria alone or of places.

- Light: cream paper, ink, and one flat colour per project section.
- Exception chosen by the owner: the folding screen's profile shadow uses an owner-supplied silhouette that is AI-generated (its C2PA marks say so); the "How this site was built" page states that.
- Must not look like a generic AI-generated site.
- Learning material behind the AI section is never credited or presented as formal study; its wording, prices, model opinions and unfinished material stay private, and no private project is named. AI results are described generically.

## Evidence on Hand

- Projects: Quote & Nod (formerly Dwelltrace; never link dwelltrace.com, an unrelated product) and Doorplate (formerly Homely) (full case studies, demo videos on YouTube), Guess The BPM and The Coffee Place (live sites, highlights in their sections).
- Marine Wobbles: native Android tap-to-pop match-3 (Kotlin, Jetpack Compose), in internal testing on Google Play. 80 levels, 27 illustrated episodes generated from her prompts, difficulty measured by seven strategy bots over seeded games. Its repo is private: never link it. No download, rating, release-date or price claims.
- Roles: Wandity (Full Stack Developer, Sept 2024–present), Bidz Labs (Front-end Architect, Web3), Aventu (freelance), CaneLab Ltd. (front-end).
- CV at public/cv.pdf; GitHub github.com/mbonete; LinkedIn in/maria-bonete.
- AI practice: an opening line naming the tools (Claude Code and Codex), then five practices (not a fixed order), each stating the problem it prevents and what she does: grilling to a shared understanding, goals that end on evidence (/goal), model and effort chosen per task, parallel agents with clear ownership, and review by a different agent. No experiment results or test figures (the owner rejected them); an example only where it can be checked. The section links to this site's public repo, where the agents' instructions and co-authored commits can be checked. The case studies don't say what agents did in each project (owner's decision, 2026-11-18).
- Absent and never to be fabricated: testimonials, client logos, usage metrics, store ratings or downloads.

## Product Principles

1. Ten seconds to "shortlist": role, three pillars and a way to act are legible in the first viewport on a phone.
2. Proof over claims: every assertion is backed by shipped work, a role, or a concrete practice.
3. The site itself is evidence of craft and of her AI workflow.
4. Honest status: unfinished work is labelled as such.

## Accessibility & Inclusion

Respect prefers-reduced-motion (loops show a still, the screen does not animate); keyboard-operable folding screen, video controls and navigation; legible contrast on every section colour.
