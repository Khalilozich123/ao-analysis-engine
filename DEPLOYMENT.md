# Deployment

This app has three parts: a **React frontend**, a **FastAPI backend**, and a **PostgreSQL**
database. Vercel is perfect for the frontend but **cannot run the backend or the database**
(Vercel only hosts static sites and short-lived serverless functions — not long-running servers,
containers, background jobs, or a database).

So the live setup is a **split**:

| Part | Host | Why |
|---|---|---|
| **Frontend** (React/Vite) | **Vercel** | Static SPA — ideal fit, always-on link. |
| **Backend** (FastAPI, Docker) | **Render** (or Railway/Fly.io) | Runs a long-lived server + background jobs. |
| **Database** (PostgreSQL) | **Render Postgres** (or Neon/Supabase) | Managed database. |

## Branch strategy
- **`main`** — development. You code here.
- **`production`** — what gets deployed. Vercel and Render watch this branch and auto-deploy on
  every push. Promote changes with: `git checkout production && git merge main && git push`.

---

## 1) Backend + database — Render

1. Push the repo to GitHub (already done).
2. **Create the database:** Render dashboard → **New → PostgreSQL** (Free). After it's created,
   copy its **Internal Database URL** (looks like `postgres://user:pass@host/db`).
3. **Create the web service:** **New → Web Service** → connect the repo →
   - **Branch:** `production`
   - **Root Directory:** `backend`
   - **Runtime:** Docker (Render uses `backend/Dockerfile` and its `CMD`; `$PORT` is injected).
4. **Environment variables** (Service → Environment):
   | Key | Value |
   |---|---|
   | `DATABASE_URL` | the Render URL, **with the scheme changed** to `postgresql+psycopg://…` |
   | `SCORER` | `keyword` (free, no API key — recommended for a public demo) |
   | `CORS_ORIGINS` | `https://<your-project>.vercel.app` (fill in after step 2 below) |
   | *(optional, for LLM mode)* | `SCORER=llm`, `GOOGLE_API_KEY=…`, `GEMINI_MODEL=gemini-3.6-flash` |
5. Deploy. You get a URL like `https://opportunity-analysis.onrender.com`.
   Verify: open `…/health` (should return `{"status":"ok"}`) and `…/docs` (Swagger).

> Tables are created automatically on startup (`init_db`), so there's no migration step.
> **Free-tier note:** Render's free web service **sleeps after ~15 min idle** and takes ~30–60s to
> wake on the next request. For truly always-on, use a paid instance or a cron ping.

---

## 2) Frontend — Vercel

1. Vercel dashboard → **Add New → Project** → import the GitHub repo.
2. Configure:
   - **Root Directory:** `frontend`
   - **Framework:** Vite (auto-detected; build `npm run build`, output `dist`).
3. **Environment variable** (Project → Settings → Environment Variables):
   | Key | Value |
   |---|---|
   | `VITE_API_BASE` | `https://<your-backend>.onrender.com/api/v1` |
4. **Set the production branch:** Project → Settings → **Git → Production Branch = `production`**.
5. Deploy. You get a permanent link: `https://<your-project>.vercel.app` — always up.

> `VITE_API_BASE` is inlined at **build** time, so after changing it, trigger a redeploy.

---

## 3) Wire the two together
- On **Render**, set `CORS_ORIGINS` to your exact Vercel URL (e.g.
  `https://opportunity-analysis.vercel.app`) and redeploy the backend.
- On **Vercel**, set `VITE_API_BASE` to your Render URL + `/api/v1` and redeploy the frontend.
- Open the Vercel link, upload `data/sample_opportunities.xlsx`, and confirm results load.

## Everyday flow
```bash
# develop on main, then promote to production to deploy:
git checkout production
git merge main
git push            # Vercel + Render auto-deploy
git checkout main
```

## Alternative: everything on one host
If you'd rather not split, **Railway** or **Render** can host all three (backend Docker service +
managed Postgres + a static frontend). The frontend-on-Vercel split above is recommended because
Vercel's static/CDN hosting for the SPA is free, fast, and genuinely always-on.
