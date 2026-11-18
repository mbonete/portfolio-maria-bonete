"use client";

import { useEffect } from "react";

// On phones, the hero's top bar stays within reach: past the hero, scrolling down hides it and a small
// scroll up slides it back in at the top (a partially persistent header). It is the same element, so
// there is still one navigation. Its slot in the hero keeps its height while the bar is fixed, so
// nothing below it moves.
const PHONE = "(max-width: 760px)";
const NUDGE = 8; // px of scrolling in one direction before the bar reacts
const SETTLE = 220; // ms for the bar to settle back into its slot at the top

export default function StickyTop() {
  useEffect(() => {
    const top = document.querySelector<HTMLElement>(".lf-top");
    const bar = top?.querySelector<HTMLElement>(".lf-top-bar");
    const hero = top?.closest<HTMLElement>(".lf-hero");
    if (!top || !bar || !hero) return;
    const phone = matchMedia(PHONE);

    let lastY = scrollY;
    let lastH = visualViewport?.height ?? innerHeight;
    let run = 0; // signed distance scrolled in the current direction
    let frame = 0;
    let settling = 0;

    // Switching between its slot and the hidden fixed bar happens at once: only the hide and show slide.
    const instantly = (change: () => void) => {
      bar.style.transition = "none";
      change();
      void bar.offsetHeight;
      bar.style.transition = "";
    };
    const unfix = () => {
      delete top.dataset.fixed;
      delete top.dataset.shown;
      top.style.height = "";
    };
    const release = () => {
      if (top.dataset.fixed === undefined) return;
      // Shown at the very top, the bar and its slot already line up: its padding and colours ease into
      // the hero's instead of switching in one frame.
      if (top.dataset.shown !== undefined && scrollY <= 0) {
        clearTimeout(settling);
        top.dataset.settling = "";
        unfix();
        settling = window.setTimeout(() => delete top.dataset.settling, SETTLE);
        return;
      }
      instantly(unfix);
    };

    const update = () => {
      frame = 0;
      const y = scrollY;
      const dy = y - lastY;
      lastY = y;
      if (!phone.matches) return release();

      if (top.dataset.fixed === undefined) {
        // Fixed from the moment its slot has scrolled out of view, hidden at first.
        if (y <= top.offsetHeight) return;
        instantly(() => {
          top.style.height = `${top.offsetHeight}px`;
          top.dataset.fixed = "";
        });
        run = 0;
        return;
      }
      // Back at the very top, it returns to its place in the hero.
      if (y <= 0) return release();
      // Chrome on Android moves the page while its own toolbar slides in or out. Those frames change
      // the visible height, and they aren't the visitor scrolling.
      const h = visualViewport?.height ?? innerHeight;
      if (h !== lastH) {
        lastH = h;
        return;
      }

      run = Math.sign(dy) === Math.sign(run) ? run + dy : dy;
      const pastHero = y > hero.offsetTop + hero.offsetHeight;
      const shown = top.dataset.shown !== undefined;
      if (run >= NUDGE) delete top.dataset.shown;
      else if (run <= -NUDGE && (pastHero || shown)) top.dataset.shown = "";
      // Inside the hero, scrolling up without it shown lets the bar in its slot come back by itself.
      else if (!pastHero && !shown && y <= top.offsetHeight) release();
    };
    const schedule = () => {
      frame ||= requestAnimationFrame(update);
    };

    schedule(); // a reload can start partway down the page
    addEventListener("scroll", schedule, { passive: true });
    phone.addEventListener("change", schedule);
    return () => {
      cancelAnimationFrame(frame);
      clearTimeout(settling);
      removeEventListener("scroll", schedule);
      phone.removeEventListener("change", schedule);
      instantly(unfix);
      delete top.dataset.settling;
    };
  }, []);

  return null;
}
