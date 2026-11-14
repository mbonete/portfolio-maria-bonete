import type { Metadata } from "next";
import { currently, person } from "@/lab/content";
import CommandPalette from "../d/_components/CommandPalette";
import LightScreen from "./_components/LightScreen";
import LightTrack from "./_components/LightTrack";
import MadridTime from "./_components/MadridTime";
import Seal from "./_components/Seal";
import Sections from "./_components/Sections";
import StickyBar from "./_components/StickyBar";
import { paletteSections, paletteWork } from "./_content";

export const metadata: Metadata = {
  title: "Maria Bonete: full-stack developer",
  description:
    "Full-stack developer in Madrid, specialising in React Native, Web3 and AI-driven engineering. Shipped work, case studies and a measured AI practice.",
};

// Each area carries one checkable fact and links to its proof, so the first viewport is evidence, not
// a list of labels. Where the fact has no room, the link still gets the visitor there.
const areas = [
  { name: "Full-stack", fact: "Next.js, Supabase and Drizzle, shipped to production", href: "#quote-and-nod" },
  { name: "Mobile", fact: "React Native with Expo, and native Kotlin", href: "#marine-wobbles" },
  { name: "Web3", fact: "Front-end architect on a trading platform", href: "#bidz-labs" },
  { name: "AI-driven engineering", fact: "Agent workflows, measured and verified", href: "#ai" },
];

export default function LabE() {
  return (
    <div className="le">
      <section className="le-hero" id="top" aria-labelledby="le-name">
        <LightScreen />

        <header className="le-top">
          <Seal label="Maria Bonete, home" />
          <nav aria-label="Primary" className="le-nav">
            <a href="#projects">Work</a>
            <a href="#ai">AI practice</a>
            <a href={person.links.cv} target="_blank" rel="noreferrer">CV</a>
            <a href={person.links.github} target="_blank" rel="noreferrer" className="le-nav-wide">GitHub</a>
            <a href={person.links.linkedin} target="_blank" rel="noreferrer">LinkedIn</a>
          </nav>
          <div className="le-cmd">
            <CommandPalette sections={paletteSections} work={paletteWork} workHeading="Work" />
          </div>
        </header>

        <div className="le-intro">
          <h1 id="le-name">Maria Bonete</h1>
          {/* Non-breaking hyphen keeps "AI-driven" on one line. */}
          <p className="le-role">{person.tagline.replace("AI-driven", "AI\u2011driven")}</p>

          <ul className="le-areas" aria-label="What I ship">
            {areas.map((a) => (
              <li key={a.name}>
                <strong>
                  <a href={a.href}>{a.name}</a>
                </strong>
                <span>{a.fact}</span>
              </li>
            ))}
          </ul>

          <div className="le-actions">
            <a className="le-primary" href="#projects">
              See the work
            </a>
            <a className="le-secondary" href={person.links.cv} target="_blank" rel="noreferrer">
              Download CV <span className="le-sr">(PDF)</span>
            </a>
          </div>
        </div>

        <div className="le-now">
          <span>{currently.role}</span>
          <span className="le-now-sep" aria-hidden />
          <span>
            Madrid <MadridTime />
          </span>
          <span className="le-now-sep le-now-light-sep" aria-hidden />
          <LightTrack />
        </div>
      </section>

      <StickyBar />
      <Sections />
    </div>
  );
}
