import { Archivo, Azeret_Mono } from "next/font/google";
import { person, projects } from "@/lab/content";
import ParticlePortrait from "./_components/ParticlePortrait";
import ProjectScenes from "./_components/ProjectScenes";
import styles from "./b.module.css";

const display = Archivo({
  subsets: ["latin"],
  axes: ["wdth"],
  variable: "--font-b-display",
});

const mono = Azeret_Mono({
  subsets: ["latin"],
  variable: "--font-b-mono",
});

export default function LabB() {
  return (
    <div className={`${styles.root} ${display.variable} ${mono.variable}`}>
      <header className={`${styles.topbar} ${styles.mono}`}>
        <a href="#top" className={styles.mark}>
          MB
        </a>
        <nav className={styles.topnav} aria-label="Primary">
          <a href="#work">Work</a>
          <a href={person.links.cv}>CV</a>
          <a href={person.links.github} target="_blank" rel="noreferrer">
            GitHub
          </a>
        </nav>
      </header>

      <ParticlePortrait src={person.cutout} />

      <section id="top" className={styles.hero}>
        <div className={styles.heroText}>
          <p className={`${styles.heroMeta} ${styles.mono}`}>
            <span>Portfolio</span>
            <span>Based in {person.location}</span>
          </p>
          <h1 className={styles.name}>
            <span>Maria</span>
            <span>Bonete</span>
          </h1>
          <p className={styles.tagline}>
            {person.role}, specialising in React Native, Web3 and{" "}
            <em>AI-driven engineering</em>.
          </p>
          <div className={`${styles.ctas} ${styles.mono}`}>
            <a href="#work" className={`${styles.btn} ${styles.btnPrimary}`}>
              Selected work <span aria-hidden>↓</span>
            </a>
            <a href={person.links.cv} className={styles.btn}>
              CV — PDF
            </a>
          </div>
        </div>
        <div className={`${styles.scrollCue} ${styles.mono}`} aria-hidden>
          Scroll
        </div>
      </section>

      <div id="work" className={`${styles.workHead} ${styles.mono}`}>
        <h2>Selected work</h2>
        <span>({String(projects.length).padStart(2, "0")})</span>
      </div>

      <ProjectScenes projects={projects} />

      <footer className={`${styles.footer} ${styles.mono}`}>
        <span>© {new Date().getFullYear()} {person.name}</span>
        <nav aria-label="Elsewhere">
          <a href={person.links.github} target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href={person.links.linkedin} target="_blank" rel="noreferrer">
            LinkedIn
          </a>
          <a href={person.links.cv}>CV</a>
        </nav>
      </footer>
    </div>
  );
}
