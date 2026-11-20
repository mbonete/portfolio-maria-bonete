---
version: 1
slug: "src-app-blog-slug-page-tsx"
primary_target: "src/app/blog/[slug]/page.tsx"
related_targets: ["src/app/blog/page.tsx"]
---

# Blog: articles and the list of articles

Scope: `/blog/[slug]` (each article) and `/blog` (the list). Mode: Read. Code-led (no image generation).

Audience and job: recruiters and hiring managers who open an article to judge depth in about a minute; developers who read on. The rules are listed up front and each is short; the detail follows.

Proof and content: the articles in `src/articles` (Markdown, figures as `![alt](src "caption")`); real Marine Wobbles screens captured from the debug build (coin screen states, lesson and test levels, the map). No invented claims; every caption traceable to the article or the game's files.

Constraints: the portfolio's world stays (cream paper, ink, one flat colour per project, Hina Mincho + Instrument Sans, the rendered phone frame); the Blog link is in the home top bar on desktop and phones; an article leads back to `/blog`. Owner rejected: chart and coin-pack art as thumbnails; the case-study look (big coloured head, huge serif headings); loose spacing; rules not standing out.

## Direction contract

THESIS: The article reads beside the game. A phone on the project's colour stays in view and shows the screen each rule is about, so a reader skimming the rules sees the product doing it. Refuses the category default: a centred column under a hero image.

OWN-WORLD: Cream paper #f6f0e3 and ink #17130f carry the reading column; Marine Wobbles blue #63bdea owns a full-height side panel; the rendered phone frame from the home bands holds the screen; Hina Mincho for the title, rule headings and rule numerals; Instrument Sans for text; a gold #c9a35f hairline marks the current rule; the lavender close band ends the page.

STORY: The reader sees the title, intro and every rule as a numbered list in the first viewport, picks a rule or scrolls, watches the phone change to that rule's screen, and leaves knowing she built and reasoned about a real app. Next: back to the blog, the case study, email.

FIRST VIEWPORT: Desktop 1440x900: left 36% sticky blue panel, phone about 280px wide centred, the screen's caption under it; right, top bar (Back to the blog / Maria Bonete), title about 52px, byline, intro at 19px, the numbered rules as links with the current one marked, rule 1 starting at the fold. Phone 390: top bar, title, byline, intro, a blue band with the phone at about 200px, then the rules; each rule's screen sits inline above its text.

FORM: Phone beside the text, 5th of 6 on the ordered list (1 rules up front, 2 explainer with key points, 3 margin notes, 4 technical note, 5 phone beside the text, 6 field guide plates). seed:bfdc9b7ce2d29f44. Signature interaction: as a rule's section reaches the reading line, the phone crossfades to its screen (200ms; instant under reduced motion) and the list marks that rule. The list page: one row per article, its lead screen in the phone on the project's colour, title, byline, summary and the rules as a short numbered list.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- Article dates are set to the push date when published.
