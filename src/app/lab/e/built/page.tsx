import type { Metadata } from "next";
import TransitionLink from "../_components/TransitionLink";

export const metadata: Metadata = { title: "How this site was built" };

const steps = [
  {
    title: "Decided by grilling, not by default",
    body: "An agent interviewed me in rounds, proposed a recommended answer to every question, and I decided. Audience first: recruiters and hiring managers who give a portfolio ten seconds, often on a phone. Then the constraints: dark only, free fonts, and above all, it must not look like another AI-generated site.",
  },
  {
    title: "A banned list before any pixels",
    body: "Gradient text, purple-to-cyan, glow blobs, dot grids, glassmorphism, Inter or Geist as the voice, pill buttons, a centred column of identical sections, “Hi, I'm” heroes, an icon by every label, and a badge above the name.",
  },
  {
    title: "Five prototypes, judged at real size",
    body: "Each direction was built as an unlinked route with real content and checked on a laptop and a phone: Instrument, Immersive, Hybrid, Drench, and the Gold Screen you landed on. Prototype code is throwaway; the winner is rebuilt cleanly.",
  },
  {
    title: "A hero rendered, not generated",
    body: "The screen is a Blender scene: four gold-leaf panels with an indigo silk mount in a dark lacquer room. The plum branch, blossoms, gold mist and violet stream are painted by a script that rasterises bristle-brush strokes, pooled ink included. The shadow is cast from a profile silhouette I chose; that one image is AI-generated, and its provenance record says so.",
  },
  {
    title: "One scene, four lamps",
    body: "The same render exists under gold, sunset, dusk and daylight lamps. The page blends between them at a constant pace, the accent colour follows, and the light track lets you stop on any light. It respects reduced motion and pauses off screen.",
  },
  {
    title: "Verified like any other change",
    body: "Every iteration was checked in a real browser at desktop and phone sizes, with lint, type checks and a design detector, and the motion was timed in the page rather than trusted from the code.",
  },
];

export default function BuiltPage() {
  return (
    <div className="le le-page">
      <header className="le-page-top">
        <TransitionLink href="/lab/e" className="le-back">
          Back to the site
        </TransitionLink>
      </header>
      <main className="le-cs">
        <div className="le-cs-head">
          <h1>How this site was built</h1>
          <p className="le-lede">
            The site is its own small case study in the way I work with agents: decisions made in the open, prototypes
            judged on real screens, and nothing accepted until it was checked.
          </p>
        </div>
        <ol className="le-built">
          {steps.map((s) => (
            <li key={s.title}>
              <h2>{s.title}</h2>
              <p>{s.body}</p>
            </li>
          ))}
        </ol>
        <p className="le-aside">
          Left out on purpose: a chatbot that answers questions about me. It would be a cliché, it could make things up in
          front of a recruiter, and it would need a paid key and abuse protection.
        </p>
      </main>
    </div>
  );
}
