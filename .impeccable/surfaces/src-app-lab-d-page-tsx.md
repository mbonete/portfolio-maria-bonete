---
version: 1
slug: "src-app-lab-d-page-tsx"
primary_target: "src/app/lab/d/page.tsx"
related_targets: []
---

## Scope

POC D at /lab/d: first viewport (hero) and the Projects section, portfolio home surface. Mode: Experience. Audience: recruiters and hiring managers deciding in ten seconds, often on a phone. Action: open the work, download the CV, contact.

Two ground variants are built side by side for the owner to choose: Mediterranean blue (default) and almagre red, switchable with `?ground=red`.

## Direction contract

THESIS: One real subject owns the frame. Maria, cut from her own seaside photo, stands in front of and through her surname set edge to edge in a very tall condensed grotesque. The interface lives only at the perimeter. This refuses the category default of a split hero, a headline, two buttons and a card grid.

OWN-WORLD: The whole page is drenched in one saturated deep ground: añil blue (or almagre red), never neutral black. Bone-white type. Shadows are tinted from the ground. One condensed display family, very tall; one plain sans for reading. Tiny perimeter labels, square-cut controls, no cards, no gradients, no glow.

STORY: In one glance the visitor reads her name, sees her, and sees four equal areas: Full-stack, Mobile, Web3, AI-driven engineering. Pulling an area into the frame shows that area's proof. Scrolling reaches Projects, led by Marine Wobbles as a large real object, then the case studies.

FIRST VIEWPORT: Full-bleed ground. The surname BONETE overscales past both edges at roughly half the viewport height (amended from about 70%, which crops the surname into illegibility), behind the cutout; her shoulder overlaps and cuts the letters. Her cutout is right of centre with a soft, offset, ground-tinted shadow, and her hair moves in a slow wind. The four area tokens sit at the four edges. The name line and the role sentence are top-left. Primary action "See the work" and "CV (PDF)" are bottom-left. The nav (Work, CV, GitHub, LinkedIn), the ground switch and ⌘K are top-right. On phones the same layering holds: name and role on top, her cutout overlapping the surname, compact tokens on the edges, and the primary action at the bottom of the first screen.

FORM: User-pinned, inspired by the principles of Marina Budarina's UI work (one hero object over giant type, a drenched ground, perimeter UI, one signature interaction), with none of her motifs or compositions. Not from the ordered list. seed:d241f8679df6cd83

SIGNATURE INTERACTION: The four area tokens can be dragged into the frame, or clicked or keyboard-activated. The frame re-lights: Maria steps aside (her cutout slides right), the giant word swaps from BONETE to that area in the cleared zone, and the perimeter shows that area's proof (projects, roles, measured results). A subtle layered depth tilt follows the pointer. Hair wind is a WebGL displacement limited to the hair mask. Under reduced motion everything is static, and the tokens still work as buttons.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- The owner picks blue or red after seeing both.
- Marine Wobbles store status: in development, with no release date.
