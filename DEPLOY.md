# ☁️ Coral Compass — Deployment Guide

Two paths. Streamlit Community Cloud is easier and free; Render is a good alternative if you want a generic web service.

> **Note:** Cloud deployments cannot install the Coral CLI (it's a local-first binary). On the cloud, the app automatically uses the **DuckDB fallback** for SQL — same queries, same output. Coral integration is best demoed live in your terminal or in a recorded video. Both are first-class proof for judges.

---

## 🟢 Option 1 — Streamlit Community Cloud (recommended)

Free, zero-config, reads straight from your GitHub repo.

### Steps

1. Open https://share.streamlit.io and sign in with GitHub (`Tanya-garg10`).
2. Click **"Create app"** → **"Deploy a public app from GitHub"**.
3. Fill in:
   - **Repository:** `Tanya-garg10/Coral-Compass`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (optional):** `coral-compass` → live at `https://coral-compass.streamlit.app`
4. Click **"Advanced settings"** → **Secrets** → paste:
   ```toml
   CEREBRAS_API_KEY = "csk-..."
   # Optional:
   # AI_MODEL = "gpt-oss-120b"
   ```
5. Click **Deploy**. First build takes ~2 minutes (installs `requirements.txt`).

### What you'll see

- Sidebar: **Coral CLI: not on PATH. Using DuckDB fallback** (expected on cloud).
- Sidebar: **Cerebras detected** if the secret is set.
- **🪸 Coral SQL** tab: the "Run with Coral" button is disabled, "Run with DuckDB" works.

### Updating the deployed app

Push to `main` on GitHub. Streamlit Cloud rebuilds automatically.

### Common issues

- **Build fails on `duckdb`** — Streamlit Cloud uses Python 3.11 by default; `duckdb>=1.0.0` works. If you ever pin Python 3.12+, regenerate the lock.
- **Secrets not picked up** — secrets are read at app start. After editing them, click **Reboot app**.
- **Module not found** — make sure it's in `requirements.txt`.

---

## 🟡 Option 2 — Render

Free Web Service tier sleeps after 15 min of inactivity, then cold-starts on next request.

### Steps

1. Sign in at https://render.com with GitHub.
2. **New +** → **Web Service** → connect `Tanya-garg10/Coral-Compass`.
3. Configure:
   - **Name:** `coral-compass`
   - **Region:** closest to your judges
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:**
     ```
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```
     streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
     ```
   - **Plan:** Free
4. **Environment** tab → add:
   - `CEREBRAS_API_KEY = csk-...`
   - (optional) `AI_MODEL = gpt-oss-120b`
   - `PYTHON_VERSION = 3.11.9`
5. Click **Create Web Service**. First deploy ~3-5 minutes.
6. Live URL is shown at the top of the service page (e.g. `https://coral-compass.onrender.com`).

### Render gotchas

- Cold start on free tier is 30-60s for the first hit after sleeping.
- Streamlit needs `--server.address 0.0.0.0` to be reachable; do not skip it.
- If the service exits immediately, check logs for the actual command being run; Render sometimes adds quotes around the start command.

---

## 🔵 Option 3 — Local-only demo (Coral fully working)

Best fidelity for the live demo. Same as the README quick start:

```powershell
cd Coral-Compass
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
.\install_coral.ps1
.\coral_setup.ps1
streamlit run app.py
```

This is the only path where the **Coral CLI: detected ✅** badge and the **🪸 Run with Coral** button work — use it for your demo video.

---

## 🧪 Post-deploy smoke test

After cloud deployment, hit your live URL and verify:

1. Page loads without error.
2. **📋 Sources** tab shows both CSVs.
3. **🔗 Joined View** shows 5 rows with priorities.
4. **🪸 Coral SQL** → "Run with DuckDB" returns 5 rows.
5. **🤖 AI Plan** → "Generate plan for today" returns model output (not fallback).

If any step fails, check the platform logs (Streamlit Cloud → "Manage app" → "Logs", Render → "Logs" tab).

---

## 📝 Submission checklist

- [ ] GitHub repo URL: `https://github.com/Tanya-garg10/Coral-Compass`
- [ ] Live demo URL (Streamlit Cloud or Render)
- [ ] 3-minute demo video (see `DEMO.md`)
- [ ] Screenshot of the local Coral SQL output (proof of integration)
- [ ] Description matches what's actually shipped: file-based study sources queried via Coral, Streamlit UI, Cerebras AI plan
