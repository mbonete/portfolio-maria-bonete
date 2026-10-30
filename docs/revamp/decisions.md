# Portfolio revamp — decision log

Source material for the future "How this site was built" page. Produced by a grilling session
(agent interviews the owner, proposes a recommended answer per question, owner decides).
Public-safe: contains only decisions about this site.

## Round 1 — framing
- **Audience:** recruiters and hiring managers (full-stack / React Native / Web3 roles). Scannable in 10s; "cool" = craft, not gimmicks.
- **Scope:** restyle + restructure layouts, same core content, new features allowed.
- **Direction:** minimal-tech + terminal flavour, or immersive WebGL — undecided; settle it with POCs.
- **Hard constraint:** must not look like a generic AI-generated site.
- **Palette:** open — whatever looks best. **Theme:** dark only. **Dependencies:** anything that earns its place.

## Round 2 — method
- **POCs** as unlinked routes on a `revamp` branch, real content, judged at real size and on a phone.
- **Three concepts:** A "Instrument" (minimal tech + terminal, ⌘K), B "Immersive" (WebGL hero, scroll storytelling), C "Hybrid" (A's restraint + one shader moment).
- **Banned list (every POC):** gradient text / purple→cyan; glow blobs, dot grids, glassmorphism; Inter / Geist / Space Grotesk as primary; rounded-full everything and pill buttons; centred max-w column of identical sections; "Hi, I'm X 👋" heroes; icon-next-to-every-label; badge pill above the H1.
- **Features in scope:** ⌘K command palette; per-project case studies with View Transitions; a live "now" strip; WebGL where it earns it. Out: terminal easter egg, sound, custom cursor.
- **Mobile:** same identity, degraded effects, LCP < 2.5s on mid-range phone, reduced-motion respected.
- **Fonts:** free only, distinctive pairing per POC.

## Round 3 — details
- Retire the purple. One accent per POC, no gradients.
- Drop the laptop line-art; use a real photo, treated per POC.
- Full case studies for Dwelltrace and Homely; short entries for the rest.
- Now strip: latest public GitHub push (server-fetched, hourly), local time in Spain, a hand-edited "currently" line.
- POCs cover hero + projects + their signature only. POC code is throwaway; the winner is rebuilt cleanly and lands via PR.
- Preview on the LAN dev server; nothing pushed until a winner is picked.

## Round 4–6 — positioning
- AI becomes core identity. Tagline: *"Full-stack developer, specialising in React Native, Web3 and AI-driven engineering."*
- New **AI section** after Projects: an opening stance, five principles each backed by a measured result, and a toolkit of eight techniques (plain-language titles, tool names as mono tags).
- Real measured results are shown generically; no project names, no third-party course material.
- **Section order:** Hero → Projects → AI → Experience → About → Contact.
- **"How this site was built" page:** this log, the POCs and why one won, review + verification steps.
- Rejected: an "ask about me" chatbot (cliché, hallucination risk in front of recruiters, needs a paid key and abuse protection).

## Round 7 — the Gold Screen (POC E)
- **Hero:** a Blender render of a four-panel gold-leaf screen in a dark lacquer room; the owner's profile shadow falls across it. Painting (plum branch, blossoms, gold mist, violet stream) is procedural; the floor reflection fades into the room.
- **Light:** the same scene under four lamps (gold, sunset, dusk, daylight), blending continuously at 2.5 s per light; the page accent follows; a light track with pause/play and a reduced-motion fallback.
- **Rejected along the way:** a hair-wind video loop, a one-off lamp warm-up nobody noticed, and a brightness "glow" between lights that read as a blast.
- **Below the hero:** Work (Marine Wobbles, two case studies with View Transitions, two short entries), AI (stance, five measured principles, eight-technique toolkit), Experience, About, Contact, and this page.

## Round 8: the screen, refined (POC E)

- Painting redone at 1.5× resolution: an old plum tree in tarashikomi (pooled ink at the edge of every puddle) rising across panels 3–4 with Korin-style blossoms that shade toward the heart; the stream's current lines are thick-thin with fewer, larger curls and two spiral eddies; the mist bands are crisp tiered forms built up in gesso, with gold dust settling below them and cut squares and strips of leaf.
- Gold leaf is laid leaf by leaf: each its own tone and burnish, a little out of true, with the overlap strip showing.
- Craft: bevelled lacquer frame, L-shaped brass corner fittings with domed nails and a punched (nanako) ground.
- Reflection: the floor keeps its polish much further out, and the render frame extends below the screen (desktop 2560×2400, phone 1170×3420) with the hero framing unchanged. The page lets that floor run under the Work heading (the render layer is 150% / 135% of the hero) and dissolves it with a long mask; the phone's dark gradient was folded into the mask so nothing cuts across the reflection.
