"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";

// Overscrolling on a Mac shows the root's background past the page's edges. Paint it the colour of the
// section at the edge being pulled: the top one in the upper half of the page, the bottom one in the
// lower half. Chrome on Android paints its bottom bar with that same background, so on touch screens
// it always comes from the bottom edge, the section the bar touches.
export default function OverscrollColour() {
  // Re-measured on every page, since each one starts and ends on its own colours.
  const path = usePathname();
  useEffect(() => {
    const root = document.documentElement;
    const touch = matchMedia("(pointer: coarse)").matches;
    // The section's --edge where it sets one (a ground under grain reads darker than its colour),
    // otherwise the first full-width solid background under the point, from the element there up its
    // ancestors. Full width only: a mockup, button or card crossing the edge isn't the section's colour.
    const colourAt = (y: number) => {
      const hit = document.elementFromPoint(innerWidth / 2, y);
      const edge = hit && getComputedStyle(hit).getPropertyValue("--edge").trim();
      if (edge) return edge;
      for (let el = hit; el; el = el.parentElement) {
        if (el.getBoundingClientRect().width < root.clientWidth - 1) continue;
        const c = getComputedStyle(el).backgroundColor;
        if (c !== "rgba(0, 0, 0, 0)" && c !== "transparent") return c;
      }
      return "";
    };
    let frame = 0;
    const update = () => {
      frame = 0;
      const atTop = !touch && scrollY < (root.scrollHeight - innerHeight) / 2;
      root.style.backgroundColor = colourAt(atTop ? 1 : innerHeight - 1);
    };
    const schedule = () => {
      frame ||= requestAnimationFrame(update);
    };
    update();
    addEventListener("scroll", schedule, { passive: true });
    addEventListener("resize", schedule);
    return () => {
      removeEventListener("scroll", schedule);
      removeEventListener("resize", schedule);
      cancelAnimationFrame(frame);
      root.style.backgroundColor = "";
    };
  }, [path]);

  return null;
}
