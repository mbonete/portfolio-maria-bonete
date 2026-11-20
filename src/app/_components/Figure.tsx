import Image from "next/image";
import type { Figure as FigureBlock } from "@/blog";
import LevelTiers from "./LevelTiers";
import PurchaseFlow from "./PurchaseFlow";

// The pictures the articles use, with their sizes, so next/image can reserve their space.
const images: Record<string, { w: number; h: number }> = {
  "/blog/coin-packs.webp": { w: 1248, h: 376 },
  "/marine-wobbles/board.webp": { w: 560, h: 1120 },
};

const sizes = {
  hero: "(max-width: 1100px) 92vw, 44vw",
  body: "(max-width: 760px) 50vw, 240px",
  thumb: "(max-width: 760px) 80vw, 280px",
};

// An article's figure: a picture, or a chart or diagram the site draws ("figure:<name>"). In the head
// (hero), in the reading column (body), or small in the blog's list (thumb, no caption).
export default function Figure({ figure, variant }: { figure: FigureBlock; variant: "hero" | "body" | "thumb" }) {
  let art: React.ReactNode;
  let shape = "wide";
  if (figure.src === "figure:level-tiers") {
    art = <LevelTiers label={figure.alt} compact={variant === "thumb"} />;
    shape = "chart";
  } else if (figure.src === "figure:purchase-flow") {
    art = <PurchaseFlow />;
    shape = "diagram";
  } else {
    const size = images[figure.src];
    if (!size) throw new Error(`No size recorded for ${figure.src}`);
    if (size.h > size.w) shape = "portrait";
    art = (
      <Image
        src={figure.src}
        width={size.w}
        height={size.h}
        alt={figure.alt}
        sizes={sizes[variant]}
        priority={variant === "hero"}
      />
    );
  }

  if (variant === "thumb") return art;
  return (
    <figure className={`lf-fig lf-fig-${variant}`} data-shape={shape}>
      {art}
      {figure.caption && <figcaption>{figure.caption}</figcaption>}
    </figure>
  );
}
