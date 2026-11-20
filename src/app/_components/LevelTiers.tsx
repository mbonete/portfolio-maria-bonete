import levels from "@/articles/marine-wobbles-levels.json";

// Marine Wobbles' 80 levels as bars: each bar's height is the level's tier, and a dot under a bar marks a
// level that teaches a new mechanic. Data from the game's level file (assets/levels.json, 5 October 2026).
const tiers = ["tutorial", "easy", "medium", "hard", "peak"] as const;
type Tier = (typeof tiers)[number];
const names: Record<Tier, string> = { tutorial: "Tutorial", easy: "Easy", medium: "Medium", hard: "Hard", peak: "Peak" };

export default function LevelTiers({ label, compact = false }: { label: string; compact?: boolean }) {
  return (
    <div className="lf-tiers" data-compact={compact || undefined}>
      {!compact && (
        <ol className="lf-tiers-y" aria-hidden>
          {[...tiers].reverse().map((t) => (
            <li key={t}>{names[t]}</li>
          ))}
        </ol>
      )}
      <div className="lf-tiers-plot" role="img" aria-label={label}>
        {levels.map((l) => {
          const tier = l.tier as Tier;
          return (
            <span
              key={l.level}
              className="lf-tiers-bar"
              style={{ "--h": tiers.indexOf(tier) + 1 } as React.CSSProperties}
              data-teach={l.teach || undefined}
              title={`Level ${l.level}: ${names[tier]}${l.teach ? ", teaches a new mechanic" : ""}`}
            />
          );
        })}
      </div>
      {!compact && (
        <>
          <span className="lf-tiers-xt" aria-hidden>
            Chapter
          </span>
          <ol className="lf-tiers-x" aria-hidden>
            {Array.from({ length: 8 }, (_, i) => (
              <li key={i}>{i + 1}</li>
            ))}
          </ol>
        </>
      )}
    </div>
  );
}
