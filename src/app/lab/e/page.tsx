import { currently, person } from "@/lab/content";
import CommandPalette from "../d/_components/CommandPalette";
import LightScreen from "./_components/LightScreen";
import LightTrack from "./_components/LightTrack";
import MadridTime from "./_components/MadridTime";
import Sections from "./_components/Sections";

// Each area carries one checkable fact, so the first viewport is proof, not a list of labels.
const areas = [
  { name: "Full-stack", fact: "Next.js, Supabase and Drizzle, shipped to production" },
  { name: "Mobile", fact: "React Native with Expo, and native Kotlin" },
  { name: "Web3", fact: "Front-end architect on a trading platform" },
  { name: "AI-driven engineering", fact: "Agent workflows, measured and verified" },
];

export default function LabE() {
  return (
    <div className="le">
      <section className="le-hero" aria-labelledby="le-name">
        <LightScreen />

        <header className="le-top">
          <a className="le-seal" href="#top" aria-label="Maria Bonete, home">
            <svg viewBox="0 0 40 40" aria-hidden>
              <path d="M3.2 4.1c11-1.3 22.7-1.1 33.5-.2.9 10.7 1 21.6-.3 32.3-11 1-22.2 1.2-33.1.2C2.2 25.6 2.3 14.8 3.2 4.1Z" />
              <text x="20" y="27.5" textAnchor="middle">MB</text>
            </svg>
          </a>
          <nav aria-label="Primary" className="le-nav">
            <a href="#projects">Work</a>
            <a href="#ai" className="le-nav-wide">AI practice</a>
            <a href={person.links.cv} target="_blank" rel="noreferrer">CV</a>
            <a href={person.links.github} target="_blank" rel="noreferrer" className="le-nav-wide">GitHub</a>
            <a href={person.links.linkedin} target="_blank" rel="noreferrer">LinkedIn</a>
          </nav>
          <div className="le-cmd">
            <CommandPalette />
          </div>
        </header>

        <div className="le-intro" id="top">
          <h1 id="le-name">Maria Bonete</h1>
          {/* Non-breaking hyphen keeps "AI-driven" on one line. */}
          <p className="le-role">{person.tagline.replace("AI-driven", "AI\u2011driven")}</p>

          <ul className="le-areas" aria-label="What I ship">
            {areas.map((a) => (
              <li key={a.name}>
                <strong>{a.name}</strong>
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

      <Sections />
    </div>
  );
}
