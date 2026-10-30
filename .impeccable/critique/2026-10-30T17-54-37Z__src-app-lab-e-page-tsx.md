---
target: the revamp UI (Gold Screen, /lab/e)
total_score: 18
max_score: 36
na_heuristics: 10
p0_count: 1
p1_count: 4
target_identity: "file:/Users/mbonete/code/new-portfolio/src/app/lab/e/page.tsx"
target_fingerprint: "sha256:b7f8b94aa8d44dd239b83308c48eb88742d0811a4e3d6dfdfb79cc14e3029344"
target_path: /Users/mbonete/code/new-portfolio/src/app/lab/e/page.tsx
timestamp: 2026-10-30T17-54-37Z
slug: src-app-lab-e-page-tsx
---
# Gold Screen critique (`/lab/e`)

Method: dual-agent (A: design review · B: detector and browser evidence). Parent re-checked the repo links, laptop collision, palette stacking and font preloads.

## Design health: 18/36, Acceptable (50%)

| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | Visibility of system status | 2 | The current light is never named; 13.7-screen phone page has no position cue |
| 2 | Match with the real world | 3 | `ultracode`, `/goal` and "Command" mean little to recruiters |
| 3 | User control and freedom | 2 | Seal lands at y=171 (y=72 on phone); "Back to work" loses your place |
| 4 | Consistency and standards | 2 | Palette says "Projects", site says "Work" |
| 5 | Error prevention | 1 | Dead code links and the hero collision |
| 6 | Recognition over recall | 2 | Light track has no label; AI link hidden on phone |
| 7 | Flexibility and efficiency | 2 | ⌘K exists but breaks below the hero |
| 8 | Aesthetic and minimalist design | 3 | Hero superb; AI section runs long |
| 9 | Error recovery | 1 | Default Next 404 with no way back |
| 10 | Help and documentation | n/a | Not relevant to a portfolio |

Contrast is strong (lowest text 7.05:1 across all four lights), no horizontal overflow, zero console errors on all four pages.

## Design specificity
Split verdict. The hero is unmistakably hers. After about 1.3 screens the concept stops and the page becomes serif headings on hairline rows, a familiar dark-editorial template. Marine Wobbles is the only later moment that feels authored.
Deterministic scan: 0 findings (control fixture confirmed the detector fires). Overlay injected on three pages; nothing to draw.

## Overall impression
First screen is award-level; the rest reads like a different, safer site. Biggest opportunity: make the screen's world last to the end of the page, after fixing the real defects.

## What's working
1. Phone hero: name above, profile centre, CTA on the floor. Passes the ten-second test at 390x844.
2. Light control: pause, keyboard, no-JS fallback, gold rest under reduced motion; focus visible on all 30 tab stops.
3. "Measured" lines: real rigour, including the reviewer that checked the wrong folder.

## Priority issues

**[P0] Two proof links return 404.** `github.com/mbonete/marine-wobbles` and `/dwelltrace` return 404 anonymously (homely, guess-the-bpm, coffee-place return 200). It is Marine Wobbles' only link, and the ⌘K "Case study" rows for Dwelltrace and Homely go somewhere other than the case study. Probably private repos, so invisible while logged in. Fix: make public, or remove the links and show a demo or README excerpt. `_content.ts:60,110`, `Sections.tsx:45,73`, `work/[slug]/page.tsx:42`. Command: /impeccable harden

**[P1] Hero collides on ordinary laptops.** At 1280x720 "See the work" prints over "Full Stack Developer at Wandity"; geometry shows the same at 1536x730 and 1600x780; at 1366x650 the CTA clips. Fix: one flex column for intro and now-line; drop fact lines below about 820px tall. `e.css:188-194`, `e.css:277-281`. Command: /impeccable adapt

**[P1] ⌘K breaks once scrolled.** Palette sits in the isolated hero under `.le-main`, so page text paints through and clicks land on the page behind. 14 rows, with Marine Wobbles and /built missing. Fix: `.le-hero:has([role=dialog]) { z-index: 10 }` or portal; route rows to case studies; `--bg-3` is undefined in `.le`. Command: /impeccable harden

**[P1] No wayfinding on phone.** 11,532px page; AI practice and ⌘K hidden (`e.css:333`), nav does not persist. AI at 4,397px, Web3 proof at 8,262px, CV and LinkedIn gone until the end. Pillars are plain text and `e.css:363` hides the proof facts despite `page.tsx:15`. Fix: pillars as anchors to their proof, "AI" in phone nav, slim sticky bar with CV and contact after the hero. Command: /impeccable adapt

**[P1] The concept abandons the page.** About 7,100 phone px from AI to footer with no image. Contact is three large links; the screen never returns. Case studies and /built have no contact path; /built closes on a chatbot disclaimer. The real photo from PRODUCT.md appears nowhere in lab/e. Fix: screen band at Contact under the live lamp; real photo in About on the silk mount; contact strip on case studies and /built; collapse toolkit on phone. Command: /impeccable bolder

## Persona red flags
- Jordan: unlabelled gradient light track; "Command ⌘K" opaque.
- Riley: two 404 code links; `#top` on `.le-intro` crops the nav (`page.tsx:48`); unknown slugs get default 404; no-JS leaves dead slider, dead pause and blank clock.
- Casey: 10 of 31 tap targets under 44px (footer 20, aside 24, seal 30); `touch-action:none` on the track may pause lights when a scroll starts there (code, untested); no quick way back up.
- Recruiter on LinkedIn: first viewport works; opening a case study and returning loses their place.

## Minor observations
- [P1 if confirmed] 363 font files, 6.8 MB, about 80% of page weight, 315 preloads, 77 distinct characters. Dev server only; check production. Fix: `preload: false` or self-hosted Latin subset (`layout.tsx`).
- [P2] Homely poster has dev indicator, cursor, scrollbar and watermark baked in; Dwelltrace image soft with stray cursor.
- [P2] At 390x664 (estimated Safari height) pillars cross the silhouette's face; at 820x1180 the role line sits on the lit panel with no scrim.
- [P2] Tab cannot reach the palette's Esc button; no skip link or footer landmark.
- [P2] Now strip lacks the specified GitHub push and "currently" line.
- [P3] Trailing ◆ before wrap; right gap on phone case hero; ghost Homely image during the Dwelltrace morph; transitions still running under reduced motion; 16 `public/lab/e/*.webp.json` files publish render prompts.

Not tested: real iPhone, Safari, LinkedIn in-app browser, touch drag, production build, throttled LCP.

## Questions to consider
- If the light is the idea, why does the page stop listening once the screen scrolls away?
- Would any recruiter miss six of the eight toolkit items?
- The silhouette was the owner's choice, but on a site that says "verify the output", what does it cost that the only likeness is AI-generated?
