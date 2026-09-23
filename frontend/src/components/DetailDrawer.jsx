import { useEffect } from "react";
import { CRITERIA, verdictInfo, tint } from "../verdict.js";
import { IconClose, IconExternal } from "./icons.jsx";
import VerdictBadge from "./VerdictBadge.jsx";

export default function DetailDrawer({ result, onClose }) {
  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") onClose();
    }
    if (result) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [result, onClose]);

  const open = Boolean(result);
  const color = open ? verdictInfo(result.verdict).color : "#9a9aa4";

  return (
    <div className={`fixed inset-0 z-40 ${open ? "" : "pointer-events-none"}`} aria-hidden={!open}>
      {/* Backdrop */}
      <div
        onClick={onClose}
        className={`absolute inset-0 bg-black/50 transition-opacity duration-200 ${
          open ? "opacity-100" : "opacity-0"
        }`}
      />
      {/* Panel */}
      <aside
        className={`absolute right-0 top-0 flex h-full w-full max-w-md flex-col border-l border-border bg-surface shadow-2xl transition-transform duration-200 ease-out ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
        role="dialog"
        aria-modal="true"
      >
        {open && (
          <>
            <header className="flex items-start gap-3 border-b border-border px-5 py-4">
              <div className="min-w-0 flex-1">
                <div className="nums text-xs text-text-dim">
                  {result.opportunity_id} · {result.reference || "—"}
                </div>
                <h2 className="mt-1 text-base font-semibold leading-snug text-text">{result.title}</h2>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg p-1.5 text-text-dim transition-colors hover:bg-elevated hover:text-text"
                aria-label="Fermer"
              >
                <IconClose />
              </button>
            </header>

            <div className="flex-1 overflow-y-auto px-5 py-5">
              {/* Verdict + score */}
              <div className="flex items-center justify-between">
                <VerdictBadge verdict={result.verdict} />
                <div className="text-right">
                  <span className="nums text-2xl font-semibold" style={{ color }}>
                    {result.score}
                  </span>
                  <span className="text-sm text-text-dim">/100</span>
                </div>
              </div>
              <div className="mt-2 text-xs text-text-muted">
                Action recommandée : <span className="text-text">{result.action}</span>
              </div>

              {/* Meta */}
              <dl className="mt-5 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
                <Meta label="Organisme" value={result.client} />
                <Meta label="Ville" value={result.city} />
                <Meta label="Budget" value={result.budget} />
                <Meta label="Caution" value={result.deposit} />
              </dl>

              {/* Subscores */}
              <h3 className="mt-6 text-xs font-medium uppercase tracking-wide text-text-dim">
                Sous-scores
              </h3>
              <ul className="mt-3 flex flex-col gap-3">
                {CRITERIA.map((c) => {
                  const val = result.subscores?.[c.key] ?? 0;
                  return (
                    <li key={c.key}>
                      <div className="flex items-baseline justify-between text-sm">
                        <span className="text-text-muted">{c.label}</span>
                        <span className="nums text-text">
                          {val}
                          <span className="text-text-dim"> / {c.max}</span>
                        </span>
                      </div>
                      <span
                        className="mt-1.5 block h-1.5 overflow-hidden rounded-full"
                        style={{ backgroundColor: tint(color, 0.14) }}
                      >
                        <span
                          className="block h-full rounded-full"
                          style={{ width: `${(val / c.max) * 100}%`, backgroundColor: color }}
                        />
                      </span>
                    </li>
                  );
                })}
              </ul>

              {/* Rationale */}
              <h3 className="mt-6 text-xs font-medium uppercase tracking-wide text-text-dim">
                Justification
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-text-muted">{result.rationale}</p>

              {/* Sources */}
              {result.sources?.length > 0 && (
                <>
                  <h3 className="mt-6 text-xs font-medium uppercase tracking-wide text-text-dim">
                    Sources ({result.sources.length})
                  </h3>
                  <ul className="mt-2 flex flex-col gap-1.5">
                    {result.sources.map((s, i) => (
                      <li key={i}>
                        <a
                          href={s}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex max-w-full items-center gap-1.5 text-sm text-accent hover:underline"
                        >
                          <IconExternal width={14} height={14} />
                          <span className="truncate">{s.replace(/^https?:\/\//, "")}</span>
                        </a>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          </>
        )}
      </aside>
    </div>
  );
}

function Meta({ label, value }) {
  return (
    <div>
      <dt className="text-xs text-text-dim">{label}</dt>
      <dd className="nums mt-0.5 text-text">{value || "—"}</dd>
    </div>
  );
}
