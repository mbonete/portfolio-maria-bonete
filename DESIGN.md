---
name: Maria Bonete
description: One crafted object on one flat colour, its name set large, a few facts.
colors:
  ink: "#17130f"
  paper: "#f6f0e3"
  gold: "#c9a35f"
  azurite: "#6581df"
  lavender: "#a99ddf"
  light-ink: "#fbf5e9"
  band-marine: "#63bdea"
  band-terracotta: "#b4492c"
  band-forest: "#1f6b4c"
  band-ultramarine: "#2b3ae0"
  band-wine: "#7c212f"
  band-deep-sea: "#18557a"
  band-bordeaux: "#551822"
typography:
  display:
    fontFamily: "Hina Mincho, serif"
    fontSize: "calc(max(3.4rem, min(18.5vw, (100svh - 160px) / 3.7, 24rem)) * 0.95)"
    fontWeight: 400
    lineHeight: 0.75
    letterSpacing: "-0.035em"
  headline-case:
    fontFamily: "Hina Mincho, serif"
    fontSize: "clamp(3.6rem, 13vw, 13rem)"
    fontWeight: 400
    lineHeight: 0.88
    letterSpacing: "-0.025em"
  headline-band:
    fontFamily: "Hina Mincho, serif"
    fontSize: "clamp(3.2rem, 10.5vw, 11rem)"
    fontWeight: 400
    lineHeight: 0.9
    letterSpacing: "-0.025em"
  headline-section:
    fontFamily: "Hina Mincho, serif"
    fontSize: "clamp(3rem, 8vw, 7.5rem)"
    fontWeight: 400
    lineHeight: 0.92
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Hina Mincho, serif"
    fontSize: "clamp(2rem, 3.6vw, 3.25rem)"
    fontWeight: 400
    lineHeight: 1.04
    letterSpacing: "-0.015em"
  title-link:
    fontFamily: "Hina Mincho, serif"
    fontSize: "clamp(1.75rem, 3.4vw, 2.75rem)"
    fontWeight: 400
    lineHeight: 1.15
  body:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  body-reading:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.62
  label:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.45
rounded:
  hairline: "2px"
  pill: "6px"
  window: "10px"
  round: "50%"
spacing:
  gutter: "clamp(20px, 5vw, 88px)"
  column-gap: "clamp(24px, 4vw, 72px)"
  band: "clamp(56px, 7vw, 112px)"
  section: "clamp(96px, 12vw, 176px)"
components:
  button-primary:
    backgroundColor: "color-mix(in oklab, #17130f 86%, #6581df)"
    textColor: "{colors.paper}"
    rounded: "{rounded.hairline}"
    padding: "0 22px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "color-mix(in oklab, #17130f 74%, #6581df)"
  button-band:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.hairline}"
    padding: "0 22px"
    height: "44px"
  button-band-dark:
    backgroundColor: "{colors.light-ink}"
    textColor: "{colors.ink}"
    rounded: "{rounded.hairline}"
    padding: "0 22px"
    height: "44px"
  link-display:
    textColor: "{colors.ink}"
    typography: "{typography.title-link}"
  play-disc:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.round}"
    size: "clamp(56px, 6.4vw, 92px)"
  browser-window:
    backgroundColor: "#fbfaf7"
    rounded: "{rounded.window}"
  nav-fixed-narrow:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
---

# Design System: Maria Bonete

## Overview

**Creative North Star: "The Object on Its Ground"**

Every surface repeats one formula: a crafted object (a studio rendered in Blender in the hero, the real product in a rendered phone or browser window for each project) set on one flat colour, its name set very large in a single-weight Mincho, and a few facts in a plain sans beside it. Colour is spent in whole fields, never in gradients or tints: azurite for the hero, one flat ground per project, ink for the index and the AI section, lavender for the closing contact, cream paper for reading. The objects carry the only depth; the grounds stay flat.

Density is low at the top of each section and rises where the reading starts. Bands and heads are large-type posters; case-study sections and blog articles settle onto paper in a two-column reading layout, the heading or the product held beside the text. Hairline rules in ink or paper at 18 to 30 percent opacity divide lists and sections; there are no cards and no boxed panels.

Links are underlined text, and the underline is the interaction: it appears, moves further from the letters, or thickens on hover. Only the main way into a section is a filled button, and it is a near-square ink block.

**Key Characteristics:**
- One flat colour per section, edge to edge; the section's ink flips to light on dark grounds.
- Hina Mincho at 400 for names, headings, numerals and the closing links; Instrument Sans for everything else.
- Real objects (the Blender-rendered studio, phone frame, browser window) carry soft cast shadows; nothing else is lifted.
- Hairline dividers and underlines instead of cards, chips or icons.
- Gold appears only as a fitting: a 1-2px line marking a current or fixed state.

## Colors

A warm ink-on-cream base with whole fields of saturated colour, one per section, and gold kept to hairlines.

### Primary
- **Azurite** (`azurite`): the hero's ground, under a fractal-noise grain on the ground only. The blue the Rinpa painters laid beside gold leaf. Its measured edge tone under grain (#5c76cc) is used only to match the overscroll band.

### Secondary
- **Lavender** (`lavender`): the closing ground. Ends the home page (contact) and every case study, the blog list and every article (the end links).

### Tertiary
- **Screen Gold** (`gold`): the gold of the screen's fittings. Used only as a line: the bottom border of the fixed narrow top bar, and the 2px inset underline on the current rule in an article's contents.

### Project grounds
Each project owns one flat ground, used for its home band, its case-study head and top bar, and any article or blog tile about it. `data-tone="dark"` grounds switch the section ink to Light Ink.
- **Marine Blue** (`band-marine`, light tone): Marine Wobbles.
- **Terracotta** (`band-terracotta`, dark tone): Quote & Nod.
- **Forest** (`band-forest`, dark tone): Doorplate.
- **Ultramarine** (`band-ultramarine`, dark tone): Guess The BPM.
- **Wine** (`band-wine`, dark tone): The Coffee Place.
- **Deep Sea** (`band-deep-sea`, dark tone): Prompt Beach. The open water in its sunset look.
- **Bordeaux** (`band-bordeaux`, dark tone): Studiolo. Darker than Wine, so the two don't read as one colour.

### Neutral
- **Ink** (`ink`): text on light grounds; the ground of the work index, the AI section, the numbers strip and the footer; the fill of buttons on light grounds; selection background.
- **Paper** (`paper`): the reading ground (case-study sections, blog), the page behind the site, button labels on ink.
- **Light Ink** (`light-ink`): text on dark project grounds, and the button fill there.
- Quieter text is always a `color-mix` of the current ink toward the current ground (72 to 84 percent ink), never a separate grey. Small text on dark grounds keeps the full Light Ink to hold 4.5:1.

### Named Rules
**The One Ground Rule.** A section is one flat colour, edge to edge. A project's colour belongs to that project everywhere it appears, and no section mixes two grounds.

**The Gold Is a Fitting Rule.** Gold is never a fill, a text colour or a ground. It is a 1-2px line marking state, and only on ink or paper; on the project blues it has no contrast, so the current state there is marked in full ink.

## Typography

**Display Font:** Hina Mincho (with serif)
**Body Font:** Instrument Sans (with system-ui, sans-serif)

**Character:** A Japanese-Mincho Latin with one weight, set huge and tight, against a neutral grotesque. Hina Mincho has no bold and no italic, and `font-synthesis: none` forbids the browser from faking either.

### Hierarchy
- **Display** (400, sized from one unit shared with the studio and bounded by the window's height, line-height 0.75, -0.035em): the name in the hero only. The studio keeps the same place under the letters at every width.
- **Headline** (400, line-height 0.88 to 0.92, -0.02 to -0.025em): project names on the bands (`headline-band`), case-study titles (`headline-case`), section titles such as Work, Experience and Get in touch (`headline-section`; the contact title runs larger, to 12rem).
- **Title** (400, 1.04 line-height): sticky case-study section headings; article titles (clamp(2.2rem, 3.7vw, 3.35rem)); rule headings in articles (clamp(1.55rem, 2.1vw, 1.9rem), 1.14).
- **Display links** (`title-link`): the contact links and the end links of every inner page, set in the display face and underlined.
- **Numerals**: rule and chapter numbers, the case-study numbers strip (to 4.75rem) and the purchase-flow steps are in the display face with lining figures.
- **Body** (400, 1rem, 1.55): default text. Case-study body 1.0625rem in a 34em column; article text 1.125rem/1.62 in a 68ch column (1.0625rem under 760px); ledes and intros 1.125-1.375rem.
- **Label** (0.875rem): top bars, stack lines, captions, dates and table heads. Weight 600 only for facts terms, status lines, table heads and the current rule; 500 for button labels.

### Named Rules
**The One Weight Display Rule.** The display face is always 400. Hierarchy in display type comes from size and tight leading, never from weight or italic.

**The Sentence Case Rule.** No uppercase, no tracked-out labels. Letter-spacing is only ever negative, on display sizes.

## Layout

A full-bleed stack of sections, each its own ground, padded by one fluid gutter (`spacing.gutter`) on both sides. Inside, a 5:7 two-column grid with a fluid column gap (`spacing.column-gap`) is the recurring split: the work index (title beside list), every band (copy beside object, under a full-width name), every case-study section (sticky heading beside the body). Poster sections (AI, experience, contact) take `spacing.section` vertical padding; bands and case heads take `spacing.band`.

The hero is a frame, not a stack: top bar in the top corners, name and studio filling the middle, role and the primary button on one baseline in the bottom corners, all sized from one unit tied to the window's height.

The blog article is the reading form of the same split: from 900px a sticky full-height panel of the project's ground at 36% holds the phone (at most 300px wide) beside a reading column on paper; below 900px each rule's screen sits inline in a band of the project's colour that crops the phone. The blog list is one row per article: a tile of the project's ground with the phone, then title, byline, summary and the numbered rules, which move into a third column from 1100px.

Breakpoints: 1100px (work index and blog rows reflow; AI heading grid), 900px (article side panel), 760px (single column everywhere; bands stack title, object, copy; the top bar becomes a fixed ink bar that hides on scroll down). Coarse pointers get 44px minimum targets on every top-bar and inline link.

### Named Rules
**The Beside Rule.** On wide screens, the thing being explained stays beside the reading: the case-study heading sticks at 24px, the article's phone sticks full height. Neither floats over the text.

## Elevation & Depth

Grounds are flat; depth belongs to the objects placed on them. The phone frame, the browser window, the case-study video and the play disc carry soft, two-layer drop shadows that read as a real object resting on the ground; the hero's folding screen carries its own rendered shadow. Grain is applied to the hero's ground only, never to the object.

### Shadow Vocabulary
- **Handset** (`box-shadow: 0 28px 40px -14px rgb(0 0 0 / 0.42), 0 8px 14px -6px rgb(0 0 0 / 0.28)`): cast by the phone body's outline.
- **Window** (`box-shadow: 0 40px 70px -30px rgb(0 0 0 / 0.5), 0 10px 24px -12px rgb(0 0 0 / 0.35)`): the browser window and the full-width case-study video.
- **Disc** (`box-shadow: 0 18px 40px -14px rgb(0 0 0 / 0.55), 0 4px 10px -4px rgb(0 0 0 / 0.3)`): the cream play disc.

### Named Rules
**The Objects Only Rule.** Shadows belong to rendered or physical objects (phone, window, video, disc). Text, buttons, lists and sections never cast one.

## Shapes

Nearly square. Buttons and chart bars take a 2px corner (`rounded.hairline`); the browser window and case video take 10px (`rounded.window`); the browser URL field 6px; the play disc and window dots are round. The phone keeps the proportions of the rendered handset (75 by 140, screen radius 11.5% / 5.76%). Lines are 1px hairlines; the only thicker strokes are the 2px state underlines and the purchase-flow track. Play and stop marks are drawn in CSS (a triangle from borders, an 8px square), never glyphs or icon fonts.

## Components

### Buttons
Few, flat and nearly square: one per section, the way in.
- **Shape:** 2px corners, 44px tall, 22px side padding, label at 500.
- **Primary (hero):** ink with a little of the hero's ground mixed in, so a solid block matches the name's thin strokes; paper label. Hover mixes in more ground.
- **Band and case-study play:** the section's ink as the fill, the opposite ink as the label (paper on ink, ink on Light Ink). The case-study play button leads with a CSS triangle and the duration at 70% opacity.
- **Hover / Focus:** 200ms background change on the shared ease. Focus is a 2px currentColor outline at 4px offset everywhere.

### Links
- **Inline and band links:** underlined at 1px, 5px offset; the offset grows to 8px on hover (220ms).
- **Top bar links:** underline hidden until hover (transparent decoration fading in).
- **Display links:** the contact and end links, in the display face, 8px offset growing to 12px.
- **Reading links (articles):** 3px offset; thickens to 2px on hover.

### Lists and dividers
- **Work index:** on ink; a hairline at 22% paper above and below each row; a 14px colour swatch and tabular number, the project name in the display face, its kind on the right.
- **Numbered lists** (chapters, steps, article contents, blog rules): a display-face numeral in a fixed first column (1.8-2.4rem), hairline borders at 18-22% ink.
- **Facts and tables:** label column at 600, hairline rows, tabular figures.
- **Bulleted lists:** an en dash marker.

### Navigation
- **Top bar:** label size, in the section's ink, links spread to the corners. Inner pages: a back link on the left, the site name or page kind on the right.
- **Narrow fixed bar:** past the hero on phones, the bar fixes to the top in ink with a gold bottom line (the screen's black lacquer frame and gold fittings), hides until a scroll up or focus, and eases back into the hero (300ms).
- **End links:** every inner page closes with a lavender band of display links (next, all articles, CV, email, LinkedIn).

### Phone and browser frames (signature)
The real product, never a mock: screenshots or a silent loop in the rendered phone frame, or the site in a neutral browser window (three neutral dots, centred URL, warm off-white chrome) with the phone standing at its right corner. On bands, phones stand in a staggered row of three, the lead one larger. While a demo plays, the phone steps down out of the way (520ms).

### Play disc
A cream disc with an ink triangle over a light ink wash; on hover the wash lifts and the disc scales to 1.06. Used on band screens and case-study posters; focus ring in paper.

### Article stage
On wide screens the sticky panel shows one screen per rule; as a rule reaches the reading line the screen crossfades (220ms) and both the contents (gold underline) and the panel's rule numbers (full ink underline) mark it.

### Status line
A project's honest status ("In internal testing on Google Play") at 600 weight in the copy.

## Do's and Don'ts

### Do:
- **Do** give every new section one flat ground from the palette, and give a new project its own ground and tone.
- **Do** set names, headings, numerals and closing links in Hina Mincho at 400, large and tight (line-height under 1 at headline sizes).
- **Do** show the real product in the phone or browser frame on the project's ground.
- **Do** derive quiet text by mixing the current ink toward the current ground, and keep full Light Ink for small text on dark grounds.
- **Do** use underlines as the link affordance and animate only their offset, thickness or colour, on `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Do** keep a 44px target on buttons and on every link under a coarse pointer, and drop all transitions under reduced motion.

### Don't:
- **Don't** use gradients, tints or textures on grounds, except the hero's grain.
- **Don't** use gold as a fill, text colour or on a blue ground.
- **Don't** put shadows on text, buttons, lists or sections; only objects cast them.
- **Don't** add cards, chips, pills or boxed panels; divide with hairlines.
- **Don't** bold or italicise the display face, or let the browser synthesise either.
- **Don't** add uppercase or letter-spaced labels, or a small invented label above a heading.
- **Don't** use icon glyphs or icon fonts; draw the few marks needed (play, stop) in CSS.
