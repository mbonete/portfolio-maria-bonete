"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";

// Overscrolling on a Mac shows the root's background past the page's edges. Paint it the colour of the
// section at the edge being pulled: the top one in the upper half of the page, the bottom one in the
// lower half.
export default function OverscrollColour() {
  // Re-measured on every page, since each one starts and ends on its own colours.
  const path = usePathname();
  useEffect(() => {
    const root = document.documentElement;
    // The section's --edge where it sets one (a ground under grain reads darker than its colour),
    // otherwise the first solid background under the point, from the element there up its ancestors.
    const colourAt = (y: number) => {
      const hit = document.elementFromPoint(innerWidth / 2, y);
      const edge = hit && getComputedStyle(hit).getPropertyValue("--edge").trim();
      if (edge) return edge;
      for (let el = hit; el; el = el.parentElement) {
        const c = getComputedStyle(el).backgroundColor;
        if (c !== "rgba(0, 0, 0, 0)" && c !== "transparent") return c;
      }
      return "";
    };
    let frame = 0;
    const update = () => {
      frame = 0;
      const atTop = scrollY < (root.scrollHeight - innerHeight) / 2;
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
