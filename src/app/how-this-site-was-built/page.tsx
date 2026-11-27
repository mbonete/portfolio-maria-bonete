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
    body: "An agent interviewed me in rounds, recommending an answer to every question, and I made the calls, from who the site is for to constraints such as free fonts only.",
  },
  {
    id: "prototypes",
    title: "Six prototypes, judged at real size",
    body: "Each direction was built as an unlinked page with real content and checked on a laptop and a phone. The sixth, one crafted object on one flat colour per project, became this site; the other five were deleted.",
  },
  {
    id: "hero",
    title: "A hero rendered in Blender",
    body: "The studio under my name introduces me through the things I like: Japanese art in the gold folding screen, photography and reading in the camera and the books, music in the conga and maracas, painting in the easel, and my own projects on the monitors. Eight things in it answer a click with a recording. I modelled the room in Blender with Python, and its textures and sounds are public domain.",
  },
  {
    id: "screens",
    title: "Real products on every project",
    body: "Each project shows its actual product. The short loops in the phones were recorded from the live sites by a script that plays them in a phone-sized browser, or cut from my game's trailer, and the phone itself is a frame I rendered rather than a downloaded mockup. Demo videos play in place and load nothing from YouTube until you press play.",
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

        {/* The steps are short, so they sit in a grid, each title right above its text, rather than one
            full-width band each with the title far from the text. */}
        <div className="lf-steps">
          {steps.map((s) => (
            <section key={s.id} aria-labelledby={s.id}>
              <h2 id={s.id}>{s.title}</h2>
              <p>{s.body}</p>
            </section>
          ))}
        </div>

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
