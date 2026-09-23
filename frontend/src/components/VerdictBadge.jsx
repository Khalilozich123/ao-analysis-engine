import { tint, verdictInfo } from "../verdict.js";

export default function VerdictBadge({ verdict }) {
  const { color } = verdictInfo(verdict);
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium whitespace-nowrap"
      style={{ color, backgroundColor: tint(color, 0.12) }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />
      {verdict}
    </span>
  );
}
