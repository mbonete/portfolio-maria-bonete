"use client";

import Image from "next/image";
import { useEffect, useRef } from "react";
import type { Project } from "@/lab/content";
import styles from "../b.module.css";

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

export default function ProjectScenes({ projects }: { projects: Project[] }) {
  const refs = useRef<(HTMLElement | null)[]>([]);

  useEffect(() => {
    const scenes = refs.current.filter((el): el is HTMLElement => el !== null);
    const set = (el: HTMLElement, reveal: number, text: number, out: number) => {
      el.style.setProperty("--reveal", reveal.toFixed(4));
      el.style.setProperty("--text", text.toFixed(4));
      el.style.setProperty("--out", out.toFixed(4));
    };

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      scenes.forEach((el) => set(el, 1, 1, 0));
      return;
    }

    let raf = 0;
    const update = () => {
      raf = 0;
      const vh = window.innerHeight;
      for (const [i, el] of scenes.entries()) {
        const r = el.getBoundingClientRect();
        if (r.bottom < -vh || r.top > vh * 2) continue;
        // 0 when the scene's top enters from below, 1 when its pin releases.
        const t = clamp01((vh - r.top) / r.height);
        set(
          el,
          easeOut(clamp01((t - 0.08) / 0.45)),
          easeOut(clamp01((t - 0.32) / 0.28)),
          // The last scene has nothing to hand over to, so it never dims.
          i === scenes.length - 1 ? 0 : clamp01((t - 0.88) / 0.12),
        );
      }
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };

    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  const total = String(projects.length).padStart(2, "0");

  return (
    <>
      {projects.map((project, i) => (
        <section
          key={project.slug}
          ref={(el) => {
            refs.current[i] = el;
          }}
          className={styles.scene}
          aria-labelledby={`b-${project.slug}`}
        >
          <div className={styles.stage}>
            <div className={`${styles.stageTop} ${styles.mono}`}>
              <span className={styles.stageIndex}>
                {String(i + 1).padStart(2, "0")} / {total}
              </span>
              <span>{project.kind === "case-study" ? "Case study" : "Project"}</span>
            </div>

            <div className={styles.frame}>
              <Image
                src={project.image}
                alt={`${project.title} screenshot`}
                fill
                sizes="(min-width: 768px) 92vw, 100vw"
                quality={70}
              />
            </div>

            <div className={styles.stageBottom}>
              <div className={styles.titleWrap}>
                <h3 id={`b-${project.slug}`} className={styles.title}>
                  <span>{project.title}</span>
                </h3>
              </div>
              <div className={styles.copy}>
                <p className={styles.summary}>{project.summary}</p>
                <ul className={`${styles.tags} ${styles.mono}`}>
                  {project.tags.map((tag) => (
                    <li key={tag}>{tag}</li>
                  ))}
                </ul>
                <a
                  href={project.href}
                  target="_blank"
                  rel="noreferrer"
                  className={`${styles.stageLink} ${styles.mono}`}
                >
                  {project.kind === "case-study" ? "Read the case study" : "Visit"} ↗
                </a>
              </div>
            </div>
          </div>
        </section>
      ))}
    </>
  );
}
