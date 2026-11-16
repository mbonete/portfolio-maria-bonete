import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { marineWobbles as mw } from "@/content";
import CaseEnd from "@/app/_components/CaseEnd";
import CaseVideo from "@/app/_components/CaseVideo";
import LoopVideo from "@/app/_components/LoopVideo";
import Phone from "@/app/_components/Phone";

export const metadata: Metadata = {
  title: "Marine Wobbles: case study",
  description:
    "A native Android match-3 in Kotlin and Jetpack Compose: difficulty measured by strategy bots over millions of seeded games, rules ported exactly from a TypeScript prototype, and Play Billing that can't lose or double a purchase.",
};

// Every figure here comes from the game's repository (private) as of November 2026.
const numbers = [
  { n: "80", k: "levels in eight chapters" },
  { n: "7", k: "strategy bots" },
  { n: "2.2M", k: "seeded games per balance run" },
  { n: "455", k: "unit tests" },
  { n: "264", k: "recorded games replayed exactly" },
  { n: "2", k: "languages, English and Spanish" },
];

const chapters = [
  "Popping, combos and collecting",
  "Gravity, in four directions",
  "Pearls, and two-colour goals",
  "Coral",
  "Marked and deep patches",
  "Spreading patches",
  "The urchin, which blasts",
  "Stones",
];

// The contract each tier holds the bots to: the share of games the stand-in player wins.
const tiers = [
  { tier: "Tutorial", levels: 8, band: "85–95%" },
  { tier: "Easy", levels: 39, band: "70–85%" },
  { tier: "Medium", levels: 22, band: "45–70%" },
  { tier: "Hard", levels: 8, band: "25–45%" },
  { tier: "Peak", levels: 3, band: "15–25%" },
];

const bots = ["random", "decent", "greedy", "hoarder", "tiler", "collector", "breaker"];

export default function MarineWobblesCaseStudy() {
  return (
    <div className="lf lf-cs-page flex-1" style={{ "--band": "#63bdea" } as React.CSSProperties}>
      <header className="lf-cs-top">
        <Link href="/#marine-wobbles">Back to work</Link>
        <span>Case study</span>
      </header>

      <main>
        <section className="lf-cs-head" aria-labelledby="cs-h">
          <p className="lf-status">{mw.status}</p>
          <h1 id="cs-h">{mw.title}</h1>
          <p className="lf-cs-lede">
            A tap-to-pop match-3 for Android, written natively in Kotlin and Jetpack Compose. This case study covers the
            engineering: bots that measure how hard each level is, rules ported exactly from my prototype, and purchases that
            can&apos;t be lost or granted twice.
          </p>
          <CaseVideo
            id={mw.trailerId}
            title="Marine Wobbles trailer"
            label="Play the trailer"
            seconds={mw.trailerLength}
            poster={
              <Image
                src="/marine-wobbles/trailer-poster.webp"
                width={1600}
                height={900}
                alt=""
                sizes="(max-width: 760px) 92vw, 90vw"
                loading="eager"
                fetchPriority="high"
              />
            }
          >
            <span>The source is private.</span>
          </CaseVideo>
        </section>

        <dl className="lf-cs-numbers">
          {numbers.map((x) => (
            <div key={x.k}>
              <dt>{x.k}</dt>
              <dd>{x.n}</dd>
            </div>
          ))}
        </dl>

        <section className="lf-cs-sec" aria-labelledby="game">
          <h2 id="game">The game</h2>
          <div className="lf-cs-body">
            <p>
              Tap a group of matching sea creatures on a six-by-six board to pop it; the rest fall into place. Each of the
              eight chapters is built around a new mechanic, taught in its first levels and then put to work:
            </p>
            <ol className="lf-cs-chapters">
              {chapters.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ol>
            <p>
              Around the board: lives, six boosters, a coin store, and 27 illustrated episodes, each with a map whose sea
              moves, a level card and a victory scene. Eight of them have levels so far.
            </p>
          </div>
          <div className="lf-phones lf-cs-wide">
            <Phone>
              <Image src="/marine-wobbles/board.webp" width={560} height={1120} alt="Level 2: a group of purple octopuses popping for 1,500 points." sizes="(max-width: 760px) 30vw, 22vw" />
            </Phone>
            <Phone size="lead">
              <LoopVideo src="/marine-wobbles/map-sakura.mp4" poster="/marine-wobbles/map-sakura.webp" label="The Sakura Waters map, its sea moving around the island path of levels." />
            </Phone>
            <Phone>
              <Image src="/marine-wobbles/urchins.webp" width={560} height={1120} alt="Level 66: urchins and patches to clear, with 55 moves left." sizes="(max-width: 760px) 30vw, 22vw" />
            </Phone>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="shape">
          <h2 id="shape">How it&apos;s put together</h2>
          <div className="lf-cs-body">
            <p>
              The rules live in their own package of pure Kotlin, with no Android and no Compose in it: the board, gravity,
              turns, powers, coins, lives, the bots and the tuner. Everything that decides an outcome can run on a plain JVM,
              which is what makes the testing and the simulations below possible.
            </p>
            <ul className="lf-cs-points">
              <li>
                <strong>One immutable session in a StateFlow.</strong>{" "}The view model holds the game as a data class that is
                copied on every change; the UI collects it with the lifecycle.
              </li>
              <li>
                <strong>A turn is one coroutine.</strong>{" "}Pop, settle and reshuffle run in the view model&apos;s scope, so
                restarting a level cancels every pending step through structured concurrency, instead of the timer list and
                run counter the prototype needed.
              </li>
              <li>
                <strong>Few dependencies.</strong>{" "}No navigation library and no dependency injection: screens are state,
                and the only swappable service, the shop, is an interface chosen by build type.
              </li>
            </ul>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="difficulty">
          <h2 id="difficulty">Measuring difficulty with bots</h2>
          <div className="lf-cs-body">
            <p>
              Seven strategy bots ({bots.join(", ")}) call the same rule functions the game ships, so the two can&apos;t
              drift apart. Each level is played 2,000 to 5,000 times per bot from fixed seeds, and a bot
              chosen per goal type stands in for a typical player.
            </p>
            <p>
              Every tier has a contract: a band for that player&apos;s win rate, a cap on how much luck can carry the best
              play, a window for when in the move budget the win lands, a minimum gap over random play, and no drop of more
              than 30 points between neighbouring levels. Tests hold every level to its contract and every tier to being
              harder than the one before. An auto-tuner records games once per move budget, reads the win rate for any
              target without replaying them, and proposes fixes; it never edits the level file itself.
            </p>
            <table className="lf-cs-table">
              <caption>The win-rate band for each tier, and how many of the 80 levels sit in it</caption>
              <thead>
                <tr>
                  <th scope="col">Tier</th>
                  <th scope="col">Levels</th>
                  <th scope="col">Win rate</th>
                </tr>
              </thead>
              <tbody>
                {tiers.map((t) => (
                  <tr key={t.tier}>
                    <th scope="row">{t.tier}</th>
                    <td>{t.levels}</td>
                    <td>{t.band}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p>
              A full run is about 2.2 million seeded games and takes some thirteen minutes, so results are cached by content:
              each measurement is keyed by a hash of the rule sources it ran and the level&apos;s own inputs, and the cache is
              committed, so a change only pays for the levels it touches. Building this exposed a bug in the build: tests
              that read the level file directly were invisible to Gradle&apos;s up-to-date check and reported stale passes,
              until I declared the file as a task input.
            </p>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="port">
          <h2 id="port">A port that replays exactly</h2>
          <div className="lf-cs-body">
            <p>
              The game started as my React Native prototype, written in TypeScript. The Kotlin rules are a port of it, held to
              identical results:
            </p>
            <ul className="lf-cs-points">
              <li>
                The random generator is ported bit for bit, with the unsigned-arithmetic traps written down, and pinned by
                tests against values printed by the TypeScript.
              </li>
              <li>
                264 whole games recorded from the prototype (44 levels, three play styles, two seeds) replay state for state.
              </li>
              <li>
                The prototype&apos;s 220-cell win-rate table comes out identical. Insisting on that caught a speculative
                &ldquo;what if&rdquo; move that was quietly advancing the real deck.
              </li>
            </ul>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="billing">
          <h2 id="billing">Purchases that can&apos;t be lost or doubled</h2>
          <div className="lf-cs-body">
            <p>Coin packs are consumable purchases through Google Play Billing, handled in this order:</p>
            <ol className="lf-cs-steps">
              <li>Grant coins only once a purchase reports as completed.</li>
              <li>Save the new balance.</li>
              <li>Only then consume the purchase, so a crash in between can&apos;t lose money or grant twice.</li>
              <li>Treat the purchase token as the key, so the same purchase is never granted again.</li>
              <li>Re-check unfinished and pending purchases every time the game comes back to the foreground.</li>
            </ol>
            <p>
              A fake shop that can be told to succeed, wait, fail, cancel or be unreachable let the whole flow be built and
              tried on a phone before the store account existed. On the internal test track it was verified with test cards:
              approved, declined, cancelled and slow payments, each granted exactly once. Purchases are verified on the device
              rather than on a server, a trade-off I chose because the game has no accounts.
            </p>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="tests">
          <h2 id="tests">Tests</h2>
          <div className="lf-cs-body">
            <p>
              455 unit tests in 44 classes, all on the JVM, because the rules and much of the UI&apos;s logic are pure
              functions. Beyond the rules:
            </p>
            <ul className="lf-cs-points">
              <li>The turn engine runs under a virtual clock, so a whole animated turn is tested in milliseconds.</li>
              <li>
                Forty tests guard the shipped level file itself: pacing, how move budgets progress, chapter structure.
              </li>
              <li>
                The copy is typed: Spanish is a subclass of English, so a missing translation fails to compile, and a test bans
                literal strings in the UI.
              </li>
              <li>The slow balance suites are opt-in, so everyday runs stay fast.</li>
            </ul>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="craft">
          <h2 id="craft">Drawing, motion and access</h2>
          <div className="lf-cs-body">
            <ul className="lf-cs-points">
              <li>
                The board is drawn on a Compose canvas and can switch, by a debug link, between one composable per creature
                and one painted node, to compare frame times against what React Native could manage.
              </li>
              <li>The creatures are the prototype&apos;s original SVG paths, read by a small path parser of my own.</li>
              <li>
                Turning off animations in Android shortens every animation and every phase of a turn, and stops the idle
                motion.
              </li>
              <li>Spoken labels throughout, 44 dp touch targets, and text that scales up to 1.4 times.</li>
            </ul>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="art">
          <h2 id="art">The art, and the pipeline behind it</h2>
          <div className="lf-cs-body">
            <p>
              The illustrations are generated from my prompts and art direction. The work around them is code: the moving
              seas are cut out of each painted map by colour in CIE Lab, rendered as 120 frames in Blender, checked so that no
              land pixel ever moves, looped seamlessly and encoded to HEVC, for all 27 maps. The level badges sit where the
              painted trail actually runs, measured from it by colour and arc length.
            </p>
          </div>
        </section>

        <section className="lf-cs-sec" aria-labelledby="stack">
          <h2 id="stack">Stack</h2>
          <div className="lf-cs-body">
            <p className="lf-cs-stack">
              Kotlin · Jetpack Compose · Coroutines and StateFlow · Google Play Billing · kotlinx-serialization · JUnit and
              kotlinx-coroutines-test · R8
            </p>
            <p className="lf-cs-stack">Tooling: Python, Blender and ffmpeg</p>
          </div>
        </section>

        <CaseEnd slug="marine-wobbles" />
      </main>
    </div>
  );
}
