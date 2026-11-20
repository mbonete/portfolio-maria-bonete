import type { Metadata } from "next";
import Link from "next/link";
import { switchboard as s } from "@/content";
import CaseEnd from "@/app/_components/CaseEnd";
import CopyCommand from "@/app/_components/CopyCommand";
import Devices from "@/app/_components/Devices";
import { share } from "@/share";

const title = `${s.title}: open source`;

export const metadata: Metadata = {
  title,
  description: s.summary,
  ...share({ title, description: s.summary, path: `/work/${s.slug}`, image: "switchboard" }),
};

const ext = { target: "_blank", rel: "noreferrer" } as const;

// The open-source project, in the case studies' shape: its colour with the panel and the dashboard, the
// way to install it, then what it does and why it's built the way it is.
export default function SwitchboardPage() {
  return (
    <div className="lf lf-cs-page flex-1" data-tone={s.band.tone} style={{ "--band": s.band.ground } as React.CSSProperties}>
      <header className="lf-cs-top">
        <Link href={`/#${s.slug}`}>Back to work</Link>
        <span>Open source</span>
      </header>

      <main>
        <section className="lf-cs-head" aria-labelledby="cs-h">
          <h1 id="cs-h">{s.title}</h1>
          <p className="lf-cs-lede">{s.summary}</p>
          <div className="lf-cs-object">
            <Devices desktop={s.band.desktop} side={s.band.panel} />
          </div>
          <p className="lf-cs-status">{s.status}.</p>
          <div className="lf-cs-links">
            <a href={s.panelRepo} {...ext}>
              The panel on GitHub
            </a>
            <a href={s.dashboardRepo} {...ext}>
              The web dashboard on GitHub
            </a>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="install">
          <h2 id="install">Install the panel</h2>
          <div className="lf-cs-body">
            <p>
              The panel is one file, saved where cmux looks for sidebars. The last line opens it in cmux&apos;s right sidebar; to
              use it as the left sidebar, right-click the sidebar button and pick switchboard.
            </p>
            <CopyCommand command={s.install} label="Install command for the Switchboard panel" />
            <p>It needs cmux with Custom Sidebars turned on, which is the default.</p>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="does">
          <h2 id="does">What it does</h2>
          <div className="lf-cs-body">
            <p>I run several coding agents at once in cmux, each in its own workspace. Switchboard reads cmux&apos;s live list of agents and sorts them:</p>
            <ul className="lf-cs-points">
              {s.lists.map((l) => (
                <li key={l.title}>
                  <strong>{l.title}.</strong> {l.body}
                </li>
              ))}
            </ul>
            <p>
              Each row also shows the folder, the git branch, any dev-server ports and the pull request. A strip at the top counts
              how many agents were working over the last 15 minutes.
            </p>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="dashboard">
          <h2 id="dashboard">The web dashboard</h2>
          <div className="lf-cs-body">
            <p>
              cmux gives sidebars no access to files or the network, so what needs either lives in a separate local web dashboard.
              It reads Claude Code&apos;s transcripts to show each agent&apos;s recap and last reply, flags a reply that ends on a
              question, and lets me allow a command, answer a question or send a reply from the page.
            </p>
            <p>
              I checked each of those end to end against a throwaway Claude Code session: the command ran, the reply arrived and the
              answer reached the agent.
            </p>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="decisions">
          <h2 id="decisions">Decisions worth a look</h2>
          <div className="lf-cs-body">
            <ul className="lf-cs-points">
              {s.decisions.map((d) => (
                <li key={d.title}>
                  <strong>{d.title}.</strong> {d.body}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="stack">
          <h2 id="stack">Stack</h2>
          <div className="lf-cs-body">
            <p className="lf-cs-stack">
              Panel: JavaScript on cmux&apos;s sidebar runtime. Dashboard: Node.js with no dependencies, Server-Sent Events, the cmux
              CLI and socket API, and Claude Code&apos;s JSONL transcripts.
            </p>
          </div>
        </section>

        <CaseEnd slug={s.slug} />
      </main>
    </div>
  );
}
