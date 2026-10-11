# Running ReSpec

Short version: locally with two commands, or online with the **frontend on Vercel** and the
**backend on Render**, both deployed automatically from `main`. The processed pipeline results
(`data/processed/`) are in the repo, the raw BMW files are not, so Render can start the backend
straight from the repo.

## A) Locally (safest for a demo)

```bash
bash scripts/start_demo.sh        # macOS, Linux, Git Bash on Windows
```

This starts the backend on `:8000`, builds the frontend for production and serves it on `:3000`.
On Windows without Git Bash, use two terminals:

```powershell
$env:DEMO_MODUS="true"; python -m uvicorn main:app --app-dir src/backend --port 8000
cd src/frontend; npm ci; npm run build; npx next start -p 3000
```

You need a `.env` copied from `.env.example`. Without an OpenAI key, set `DEMO_MODUS=true`:
answers then come from `data/demo_cache/` and the prompt lens falls back to keyword rules.

The frontend talks to `http://localhost:8000` by default. If your backend runs elsewhere, set
`NEXT_PUBLIC_API_URL` (for example in `src/frontend/.env.local`) **before** `npm run build`,
because Next.js bakes it into the build.

## B) Online: backend on Render, frontend on Vercel

**Why two services.** The backend keeps the PM state in memory and writes `audit.db`. That needs
one process that stays alive (`core/single_process.py`). Vercel functions restart all the time,
and decisions would get lost. We dropped two alternatives: FastAPI as a Vercel function (state breaks)
and baking the data into the UI (no more decisions, weights or lens).

**Step 1: backend first, because Vercel needs its address**

1. render.com → *New* → *Blueprint* → pick the GitHub repo. Render reads `render.yaml` in the root.
2. When asked for `OPENAI_API_KEY`, enter your own key. Or leave it empty and set `DEMO_MODUS` to `true`:
   then it costs nothing, but free questions to the assistant won't work.
3. Wait until it says *Live*, then open `https://<your-service>.onrender.com/health`.
   You should see `"status":"ok"` and six scenarios.

**Step 2: frontend**

1. vercel.com → *Add New Project* → pick the repo.
2. **Root directory:** `src/frontend`. Without this, Vercel won't find Next.js.
3. **Environment variable:** `NEXT_PUBLIC_API_URL` = your Render address **without a trailing `/`**.
   Set it for production and preview. It ends up in the browser, so never put a key there.
4. Deploy. CORS already allows every `*.vercel.app` address (`CORS_ORIGIN_REGEX` in `render.yaml`).
   For a custom domain, add it to `CORS_ORIGINS` in Render.
5. After changing `NEXT_PUBLIC_API_URL`, click **Redeploy**. It is baked in at build time.

**Good to know**

- Free Render instances sleep after 15 minutes. The first request after that takes about 50 seconds.
  Open `/health` once before a demo.
- After sleeping or a new deploy, `audit.db` is empty (Render's disk is not persistent). The pipeline data stays,
  only decisions made online disappear. For a jury that is fine: everyone starts clean.
- A public link with a real key means strangers can spend your credits. Set a spending limit on the key.
- Every push to `main` deploys both. A red CI run means a broken online version.

## C) Fallback: backend from a laptop through a tunnel

If Render is down, run the backend locally and give it an https address:

```bash
cloudflared tunnel --url http://localhost:8000     # or: ngrok http 8000
```

Put the printed `https://...` address into `NEXT_PUBLIC_API_URL` on Vercel (then redeploy) and into
`CORS_ORIGINS`. Downside: the laptop has to stay on.

## D) Images and media

- Images live in `src/frontend/public/media/` (`poster.jpg`, `split.jpg`, `scenarios/<ID>.jpg`). A missing file is not an error;
  the page shows a placeholder.
- The media list is built at build time. Rebuild after adding files.

## E) Checklist before every deploy

```bash
cd src/frontend && npm run lint && npm run build     # must be green
python -m pytest -q                                  # must be green
python scripts/secret_scan.py                        # no keys
```

Then in the browser: open `/`, `/cockpit`, `/insights`, `/portfolio`, `/evidence`, `/audit`, `/benchmarks`,
check the console for errors, and apply one weight change in the cockpit. It should show up in the audit trail.
