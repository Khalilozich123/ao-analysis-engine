import { VERDICTS, tint } from "../verdict.js";
import { IconSearch, IconDownload } from "./icons.jsx";

const CLASSES = ["Fort intérêt", "À qualifier", "Faible intérêt", "Non pertinent"];
const TOPS = [
  { label: "Tous", value: null },
  { label: "Top 10", value: 10 },
  { label: "Top 25", value: 25 },
  { label: "Top 50", value: 50 },
];

export default function FilterBar({ filters, onChange, shown, total, onExport }) {
  const set = (patch) => onChange({ ...filters, ...patch });

  return (
    <div className="flex flex-col gap-3">
      {/* Row 1 — verdict chips */}
      <div className="flex flex-wrap items-center gap-1.5">
        <Chip active={!filters.verdict} onClick={() => set({ verdict: null })}>
          Tous
        </Chip>
        {CLASSES.map((v) => {
          const color = VERDICTS[v].color;
          const active = filters.verdict === v;
          return (
            <button
              key={v}
              type="button"
              onClick={() => set({ verdict: active ? null : v })}
              className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium transition-colors"
              style={{
                color: active ? color : "#9a9aa4",
                borderColor: active ? tint(color, 0.5) : "#26262b",
                backgroundColor: active ? tint(color, 0.12) : "transparent",
              }}
            >
              <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />
              {v}
            </button>
          );
        })}
      </div>

      {/* Row 2 — search, Top N, export, count */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Search */}
        <div className="relative">
          <span className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-text-dim">
            <IconSearch width={15} height={15} />
          </span>
          <input
            type="search"
            value={filters.search}
            onChange={(e) => set({ search: e.target.value })}
            placeholder="Rechercher…"
            className="w-44 rounded-lg border border-border bg-surface py-1.5 pl-8 pr-2.5 text-sm text-text placeholder:text-text-dim focus:border-text-dim"
          />
        </div>

        {/* Top N */}
        <select
          value={filters.top ?? ""}
          onChange={(e) => set({ top: e.target.value ? Number(e.target.value) : null })}
          className="rounded-lg border border-border bg-surface px-2.5 py-1.5 text-sm text-text-muted focus:border-text-dim"
        >
          {TOPS.map((t) => (
            <option key={t.label} value={t.value ?? ""}>
              {t.label}
            </option>
          ))}
        </select>

        <span className="ml-1 text-xs text-text-dim">
          {shown} sur {total} affichées
        </span>

        {/* Export */}
        <button
          type="button"
          onClick={onExport}
          className="ml-auto inline-flex items-center gap-1.5 rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-text-muted transition-colors hover:border-text-dim hover:text-text"
        >
          <IconDownload width={16} height={16} />
          Exporter Excel
        </button>
      </div>
    </div>
  );
}

function Chip({ active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full border px-2.5 py-1 text-xs font-medium transition-colors ${
        active
          ? "border-text-dim bg-elevated text-text"
          : "border-border text-text-muted hover:text-text"
      }`}
    >
      {children}
    </button>
  );
}
