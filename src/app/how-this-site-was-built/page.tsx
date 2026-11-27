import type { Metadata } from "next";
import Link from "next/link";
import { person } from "@/content";
import { share } from "@/share";

const title = "How this site was built";
const description =
  "The portfolio as a worked example of building with coding agents: decisions, prototypes, a rendered hero, real product screens and checks.";

export const metadata: Metadata = {
  title,
  description,
  ...share({ title, description, path: "/how-this-site-was-built", image: "site" }),
};

const ext = { target: "_blank", rel: "noreferrer" } as const;

// Every step here is on the record: the decision log in docs/revamp, the code, and the commits.
const steps = [
  {
    id: "grilling",
    title: "Decided in grilling rounds",
    body: "An agent interviewed me in rounds, recommending an answer to every question, and I made the calls. Audience first: recruiters and hiring managers who give a portfolio ten seconds, often on a phone. Then the constraints: free fonts only, and it must not look like another AI-generated site.",
  },
  {
    id: "banned",
    title: "A banned list before any pixels",
    body: "Gradient text, purple-to-cyan, glow blobs, dot grids, glassmorphism, Inter or Geist as the voice, pill buttons, a centred column of identical sections, “Hi, I'm” heroes, an icon by every label, and a badge above the name.",
  },
  {
    id: "prototypes",
    title: "Six prototypes, judged at real size",
    body: "Each direction was built as an unlinked page with real content and checked on a laptop and a phone. The sixth, one crafted object on one flat colour per project, became this site; the other five were deleted.",
  },
  {
    id: "hero",
    title: "A hero rendered in Blender",
    body: "The studio under my name is one Blender scene, with every object modelled in Python: the folding screen, the desk with two of my projects and this site's code on its monitors, the plush capybara, the instruments and the easel. Nine things in it answer a click, eight of them with a recording: the conga, the maracas and the capybara move, the keyboard and the computer change their lights, the camera fires its flash, a breeze goes through the monstera, and the painting on the easel, painted in code and left unfinished, moves on a stage. Each of those eight is rendered as a layer of its own from the same camera, so it can change while the rest of the room stays as it is. Clicking the monitors scrolls the code on the middle one, which also scrolls once by itself when the room appears. That code is a tall image of the file, toned to match the render and placed on the screen with a CSS matrix3d computed from the Blender camera. The textures, the environment the glossy surfaces reflect and the sounds are public domain (CC0), from Poly Haven, ambientCG and Freesound (recordings by Sassaby, Sadiquecat, stu556, Breviceps, Kodack, Eirikr, saturdaysoundguy and Garuda1982).",
  },
  {
    id: "screens",
    title: "Real products on every project",
    body: "Each project shows its actual product. The short loops in the phones were recorded from the live sites by a script that plays them in a phone-sized browser, or cut from my game's trailer, and the phone itself is a frame I rendered rather than a downloaded mockup. Demo videos play in place and load nothing from YouTube until you press play.",
  },
  {
    id: "copy",
    title: "Copy held to written rules",
    body: "The text follows writing rules kept in the repository: no contrast for effect, no slogans or marketing words, and every fact traceable to the code or my CV. Agents writing copy for this site load those rules first.",
  },
  {
    id: "checks",
    title: "Checked like any other change",
    body: "Every change was looked at in a real browser at desktop and phone sizes, with lint and type checks, and layout shift was measured on the page.",
  },
];

export default function BuiltPage() {
  return (
    <div className="lf lf-cs-page flex-1" style={{ "--band": "#6581df" } as React.CSSProperties}>
      <header className="lf-cs-top">
        <Link href="/#ai">Back to the site</Link>
      </header>

      <main>
        <section className="lf-cs-head" aria-labelledby="cs-h">
          <h1 id="cs-h">How this site was built</h1>
          <p className="lf-cs-lede">
            This site is a small case study in how I work with coding agents: decisions made in grilling rounds, prototypes
            judged on real screens, and nothing accepted until it was checked.
          </p>
        </section>

        {steps.map((s) => (
          <section key={s.id} className="lf-cs-sec" aria-labelledby={s.id}>
            <h2 id={s.id}>{s.title}</h2>
            <div className="lf-cs-body">
              <p>{s.body}</p>
            </div>
          </section>
        ))}

        <section className="lf-cs-sec" aria-labelledby="left-out">
          <h2 id="left-out">Left out on purpose</h2>
          <div className="lf-cs-body">
            <p>
              A chatbot that answers questions about me. It would be a cliché, it could make things up in front of a
              recruiter, and it would need a paid key and abuse protection.
            </p>
          </div>
        </section>

        <nav className="lf-cs-end" aria-label="More">
          <Link href="/#work">See the work</Link>
          <a href={`mailto:${person.email}`}>Email me</a>
          <a href={person.links.linkedin} {...ext}>
            Talk to me on LinkedIn
          </a>
        </nav>
      </main>
    </div>
  );
}
