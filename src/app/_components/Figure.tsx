import Image from "next/image";
import type { Figure as FigureBlock } from "@/blog";
import LevelTiers from "./LevelTiers";
import PurchaseFlow from "./PurchaseFlow";

// A figure in an article's text: a chart or diagram the site draws ("figure:<name>"). Game screens are
// not drawn here; they go in the phone (Screen.tsx and ArticleStage.tsx).
export default function Figure({ figure }: { figure: FigureBlock }) {
  let art: React.ReactNode;
  if (figure.src === "figure:level-tiers") art = <LevelTiers label={figure.alt} />;
  else if (figure.src === "figure:purchase-flow") art = <PurchaseFlow />;
  else throw new Error(`No figure called ${figure.src}`);
  return (
    <figure className="lf-fig" data-shape={figure.src.slice(7)}>
      {art}
      {figure.caption && <figcaption>{figure.caption}</figcaption>}
    </figure>
  );
}

// A game screen in the site's phone frame. The screens in public/blog/screens are full-resolution
// captures, 1080 by 2160, served at quality 90 so the game's small text stays sharp. "priority" loads
// it first; "eager" loads it without waiting for it to come into view.
export function ScreenImage({
  figure,
  sizes,
  priority,
  eager,
}: {
  figure: FigureBlock;
  sizes: string;
  priority?: boolean;
  eager?: boolean;
}) {
  return (
    <Image
      src={figure.src}
      width={1080}
      height={2160}
      alt={figure.alt}
      sizes={sizes}
      quality={90}
      priority={priority}
      loading={priority ? undefined : eager ? "eager" : "lazy"}
    />
  );
}
