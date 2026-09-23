import { BarChart, Bar, Cell, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import { VERDICTS, verdictInfo, tint } from "../verdict.js";

const ORDER = ["Fort intérêt", "À qualifier", "Faible intérêt", "Non pertinent"];

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  return (
    <div className="rounded-lg border border-border bg-elevated px-3 py-1.5 text-xs">
      <span style={{ color: p.color }}>{p.name}</span>
      <span className="ml-2 nums text-text">{p.value}</span>
    </div>
  );
}

export default function SummaryPanel({ results, total, completed, status }) {
  const counts = ORDER.map((name) => ({
    name,
    value: results.filter((r) => r.verdict === name).length,
    color: verdictInfo(name).color,
  }));
  const avg = results.length
    ? Math.round(results.reduce((s, r) => s + r.score, 0) / results.length)
    : 0;

  return (
    <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
      {/* Distribution chart */}
      <div className="card p-5">
        <div className="flex items-baseline justify-between">
          <h2 className="text-sm font-medium text-text">Répartition des verdicts</h2>
          <span className="text-xs text-text-dim">
            {status === "running" ? `Analyse ${completed}/${total}…` : `${results.length} analysées`}
          </span>
        </div>
        <div className="mt-4 h-[168px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={counts} layout="vertical" margin={{ left: 0, right: 12, top: 0, bottom: 0 }} barSize={18}>
              <XAxis type="number" hide allowDecimals={false} />
              <YAxis
                type="category"
                dataKey="name"
                width={104}
                tickLine={false}
                axisLine={false}
                tick={{ fill: "#9a9aa4", fontSize: 12 }}
              />
              <Tooltip cursor={{ fill: "rgba(255,255,255,0.03)" }} content={<ChartTooltip />} />
              <Bar dataKey="value" radius={[0, 5, 5, 0]} background={{ fill: "rgba(255,255,255,0.03)" }}>
                {counts.map((c) => (
                  <Cell key={c.name} fill={c.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Compact synthesis */}
      <div className="card flex flex-col p-5">
        <h2 className="text-sm font-medium text-text">Synthèse</h2>
        <div className="mt-4 flex items-end gap-6">
          <div>
            <div className="nums text-3xl font-semibold tracking-tight">{results.length}</div>
            <div className="text-xs text-text-dim">opportunités analysées</div>
          </div>
          <div>
            <div className="nums text-3xl font-semibold tracking-tight">{avg}</div>
            <div className="text-xs text-text-dim">score moyen</div>
          </div>
        </div>
        <ul className="mt-5 flex flex-col gap-2">
          {counts.map((c) => (
            <li key={c.name} className="flex items-center gap-2.5 text-sm">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: c.color }} />
              <span className="text-text-muted">{c.name}</span>
              <span className="nums ml-auto font-medium" style={{ color: c.value ? c.color : "#6b6b74" }}>
                {c.value}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
