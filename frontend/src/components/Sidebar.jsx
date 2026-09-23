import { IconLogo, IconGrid, IconHistory } from "./icons.jsx";

function NavItem({ icon, label, active, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors ${
        active ? "bg-elevated font-medium text-text" : "text-text-muted hover:bg-white/[0.03] hover:text-text"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

export default function Sidebar({ view, onNavigate }) {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-surface px-4 py-5 md:flex">
      <div className="flex items-center gap-2.5 px-2">
        <span className="text-accent">
          <IconLogo width={22} height={22} />
        </span>
        <div className="leading-tight">
          <div className="text-sm font-semibold">Analyse d'AO</div>
          <div className="text-xs text-text-dim">Appels d'offres</div>
        </div>
      </div>

      <nav className="mt-8 flex flex-col gap-1">
        <NavItem
          icon={<IconGrid width={17} height={17} />}
          label="Nouvelle analyse"
          active={view === "upload" || view === "results"}
          onClick={() => onNavigate("upload")}
        />
        <NavItem
          icon={<IconHistory width={17} height={17} />}
          label="Historique"
          active={view === "history"}
          onClick={() => onNavigate("history")}
        />
      </nav>

      <div className="mt-auto rounded-lg border border-border px-3 py-3 text-xs text-text-dim">
        Moteur multi-agents · LangGraph
        <div className="mt-1 text-text-muted">Scoring 0–100 · 6 critères</div>
      </div>
    </aside>
  );
}
