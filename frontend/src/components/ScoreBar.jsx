import { tint, verdictInfo } from "../verdict.js";

// Compact score cell: the number + a track filled to score/100 in the verdict color.
export default function ScoreBar({ score, verdict }) {
  const { color } = verdictInfo(verdict);
  return (
    <div className="flex items-center gap-2.5">
      <span className="nums w-7 text-right text-sm font-semibold tabular-nums" style={{ color }}>
        {score}
      </span>
      <span className="h-1.5 w-16 overflow-hidden rounded-full" style={{ backgroundColor: tint(color, 0.15) }}>
        <span
          className="block h-full rounded-full transition-[width] duration-500"
          style={{ width: `${Math.max(0, Math.min(100, score))}%`, backgroundColor: color }}
        />
      </span>
    </div>
  );
}
