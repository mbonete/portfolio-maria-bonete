import type { ReactNode } from "react";

// Test hero (branch test/hero): the studio scene, rendered in Blender, on the blue ground under the
// name. Every object finished (gate 3).
export default function StudioScene({ name, intro }: { name: ReactNode; intro: ReactNode }) {
  return (
    <>
      <div className="lf-stage lf-stage-studio">
        {name}
        <div className="lf-object lf-studio">
          {/* eslint-disable-next-line @next/next/no-img-element -- art-directed srcset, not next/image */}
          <img
            src="/studio/studio-1200.webp"
            srcSet={[1200, 1800, 2400].map((w) => `/studio/studio-${w}.webp ${w}w`).join(", ")}
            sizes="(max-width: 760px) 96vw, 80vw"
            width={2400}
            height={1162}
            alt="A studio set out on the blue ground: the gold folding screen, a potted monstera, a desk with three monitors showing Prompt Beach, a code editor and Switchboard, a computer with lit fans, a plush capybara in a scarf, a coffee tray, a stack of books with a camera on top, maracas, a conga, and an easel holding an unfinished abstract painting, a palette at its foot."
            fetchPriority="high"
            draggable={false}
          />
        </div>
      </div>
      <div className="lf-foot lf-foot-studio">{intro}</div>
    </>
  );
}
