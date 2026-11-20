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

// A game screen in the site's phone frame. The screens in public/blog/screens are 720 by 1440.
export function ScreenImage({ figure, sizes, eager }: { figure: FigureBlock; sizes: string; eager?: boolean }) {
  return <Image src={figure.src} width={720} height={1440} alt={figure.alt} sizes={sizes} priority={eager} />;
}
