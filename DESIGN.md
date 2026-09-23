# DESIGN.md — Opportunity Analysis Dashboard

Mode: **Operate** (a task dashboard; the tool disappears into the work). Visual world:
**dark, minimal "AI-native BI"** (Basedash-inspired), monochrome base + semantic verdict colors.

## Tokens (implemented in `frontend/src/index.css` + `tailwind.config.js`)
- Background `#0a0a0b`; surface `#141416`; elevated/hover `#1b1b1f`; border `#26262b`.
- Text: primary `#f4f4f5`, muted `#9a9aa4`, dim `#6b6b74`.
- Accent (focus/links/selection only): indigo `#7c83ff`.
- Verdict semantics (text / tint bg / border):
  - Fort intérêt → green `#4ade80`
  - À qualifier → amber `#fbbf24`
  - Faible intérêt → orange `#fb923c`
  - Non pertinent → red `#f87171`

## Type
- One family: **Inter** (familiar sans, Operate). Fixed rem scale (no fluid clamps), ratio ~1.2.
- Tabular figures (`tabular-nums`) for all scores/amounts.

## Rules (from the craft floor)
- Elevation declared once: border **or** shadow, not both (avoid ghost cards). Card radius 12–16px.
- Semantic color for state/action only, never decoration. Accent not used as fill on inactive.
- Full component states: default/hover/focus/active/disabled/loading/error/empty.
- Loading = skeletons, not center spinners. Empty states teach the flow.
- Detail panel is a right-side drawer via `position: fixed` (escapes overflow). Transitions 150–250ms.
- Drawn SVG icons in one stroke weight; no emoji-as-icon.

## Surfaces / flow (French UI)
Upload (drag-drop .xlsx) → live progress (poll `/results`, rows stream in) → results:
KPI row + verdict bar chart (Recharts) + ranked, sortable table
(Rang · N° · Référence · Objet · Organisme · Ville · Budget · Caution · Score bar · verdict badge)
→ row click opens detail drawer (6 sub-scores as bars, rationale, sources, recommended action).
