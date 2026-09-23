import { useState } from "react";
import ScoreBar from "./ScoreBar.jsx";
import VerdictBadge from "./VerdictBadge.jsx";
import { IconSort } from "./icons.jsx";

function formatMoney(v) {
  if (v == null || v === "") return "—";
  const s = String(v).trim();
  if (/^\d+$/.test(s)) return `${Number(s).toLocaleString("fr-FR")} MAD`;
  return s;
}

// Fixed column widths so Score + Verdict are always visible; Objet takes the remaining space.
const COLGROUP = [48, 92, 100, null, 148, 82, 116, 120, 128]; // null = flexible (Objet)
const HEADERS = ["#", "N° ordre", "Référence", "Objet", "Organisme", "Ville", "Budget"];

export default function ResultsTable({ results, total, status, onSelect, selectedId }) {
  const [desc, setDesc] = useState(true);
  const sorted = [...results].sort((a, b) => (desc ? b.score - a.score : a.score - b.score));
  const pending = Math.max(0, total - results.length);
  const skeletons = status === "running" ? Math.min(pending, 8) : 0;

  if (results.length === 0 && skeletons === 0) {
    return (
      <div className="card flex flex-col items-center justify-center px-6 py-16 text-center">
        <p className="text-sm font-medium text-text">Aucun résultat</p>
        <p className="mt-1 text-xs text-text-dim">Les opportunités analysées apparaîtront ici.</p>
      </div>
    );
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] table-fixed border-collapse text-sm">
          <colgroup>
            {COLGROUP.map((w, i) => (
              <col key={i} style={w ? { width: `${w}px` } : undefined} />
            ))}
          </colgroup>
          <thead>
            <tr className="border-b border-border text-left text-xs text-text-dim">
              {HEADERS.map((c) => (
                <th key={c} className="truncate px-4 py-3 font-medium">
                  {c}
                </th>
              ))}
              <th className="px-4 py-3 font-medium">
                <button
                  type="button"
                  onClick={() => setDesc((d) => !d)}
                  className="inline-flex items-center gap-1.5 text-text-muted transition-colors hover:text-text"
                  title={desc ? "Score décroissant" : "Score croissant"}
                >
                  Score <IconSort width={14} height={14} />
                </button>
              </th>
              <th className="px-4 py-3 font-medium">Verdict</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((r, i) => {
              const selected = r.opportunity_id === selectedId;
              return (
                <tr
                  key={r.opportunity_id + i}
                  onClick={() => onSelect(r)}
                  className={`cursor-pointer border-b border-border/60 transition-colors last:border-0 ${
                    selected ? "bg-elevated" : "hover:bg-white/[0.02]"
                  }`}
                >
                  <td className="nums px-4 py-3 text-text-dim">{i + 1}</td>
                  <td className="nums truncate px-4 py-3 text-text-muted">{r.opportunity_id}</td>
                  <td className="truncate px-4 py-3 text-text-muted">{r.reference || "—"}</td>
                  <td className="truncate px-4 py-3 text-text" title={r.title}>
                    {r.title}
                  </td>
                  <td className="truncate px-4 py-3 text-text-muted" title={r.client || ""}>
                    {r.client || "—"}
                  </td>
                  <td className="truncate px-4 py-3 text-text-muted">{r.city || "—"}</td>
                  <td className="nums truncate px-4 py-3 text-text-muted">{formatMoney(r.budget)}</td>
                  <td className="px-4 py-3">
                    <ScoreBar score={r.score} verdict={r.verdict} />
                  </td>
                  <td className="px-4 py-3">
                    <VerdictBadge verdict={r.verdict} />
                  </td>
                </tr>
              );
            })}
            {Array.from({ length: skeletons }).map((_, i) => (
              <tr key={`sk-${i}`} className="border-b border-border/60 last:border-0">
                {Array.from({ length: 9 }).map((__, j) => (
                  <td key={j} className="px-4 py-3.5">
                    <span className="skeleton block h-3.5 rounded" style={{ width: j === 3 ? "80%" : "60%" }} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
