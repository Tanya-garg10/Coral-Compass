# 🎬 Coral Compass — Demo Script (3 minutes)

A tight, judge-friendly walkthrough. Time stamps assume a 3-minute video. Read it like a teleprompter or paraphrase — keep it conversational.

---

## 🪪 Setup before you record

- Have these open in tabs/windows so you can switch fast:
  1. The Streamlit app at `http://localhost:8501`
  2. A terminal in the project folder with `coral` on PATH
  3. The GitHub repo: https://github.com/Tanya-garg10/Coral-Compass
- Make the terminal font large (Ctrl + scroll up) so SQL output is readable.
- Close noisy notifications.

---

## 0:00–0:30 — Hook & problem (30s)

> "Hi, I'm Tanya. Students juggle assignments, deadlines, and notes across half a dozen apps — Google Calendar, Notion, Drive, WhatsApp groups. Important things slip through the cracks. **Coral Compass** is a study planner that pulls all of it into one queryable layer with **Coral**, then asks an LLM to plan your day.
>
> The data lives as plain CSV files for this demo, but the same approach works for any source Coral supports."

**On screen:** Streamlit dashboard, sidebar visible.

---

## 0:30–1:00 — Architecture (30s)

> "Here's the flow: CSV files → **Coral SQL runtime** → Streamlit UI → Cerebras Llama for the actual study plan. Coral turns each CSV into a SQL table, so I can `JOIN` assignments with notes in one query — no glue code, no ETL."

**On screen:** quickly show this block from the README:

```
CSV / file sources  ──▶  Coral (SQL over files)  ──▶  Streamlit UI  ──▶  AI (study plan)
                          └── fallback: DuckDB (in-process)
```

---

## 1:00–2:00 — Coral SQL proof (60s)

> "First, the Coral integration. I registered the CSVs as a Coral source from a YAML spec — `studysync.coral.yaml` — and Coral validated it."

**Switch to terminal**, run live:
```bash
coral source list
```

> "Now I run the actual join across both file sources — through Coral, locally, with no API stitching."

```bash
coral sql "SELECT a.subject, a.assignment, a.deadline, n.note_topic
           FROM studysync.assignments a
           JOIN studysync.notes n ON a.subject = n.subject
           ORDER BY a.deadline"
```

**Expected output:**
```
+---------+------------------------+------------+-------------------------------+
| subject | assignment             | deadline   | note_topic                    |
+---------+------------------------+------------+-------------------------------+
| DBMS    | SQL Assignment         | 2026-06-02 | Joins and Indexing            |
| ML      | Model Evaluation       | 2026-06-03 | Regression                    |
| OS      | Process Scheduling Lab | 2026-06-04 | Process Scheduling Algorithms |
| AI      | Project Report         | 2026-06-05 | Neural Networks               |
| CN      | Socket Programming     | 2026-06-06 | TCP UDP Sockets               |
+---------+------------------------+------------+-------------------------------+
```

> "Five rows, joined on `subject`, sorted by deadline. That's real Coral output — same SQL the agent would write."

---

## 2:00–2:40 — Streamlit dashboard (40s)

**Switch to browser at `http://localhost:8501`.**

> "The same query powers the dashboard. Sidebar shows Coral CLI detected and Cerebras detected. Top metrics: how many assignments, how many urgent, next deadline."

**Click each tab in order:**
- **📋 Sources** — "raw CSVs side by side."
- **🔗 Joined View** — "the prioritized table — DBMS due first, color-coded urgency."
- **🪸 Coral SQL** — "users can run any SQL through Coral live, or fall back to DuckDB. Same query, both engines."

---

## 2:40–3:00 — AI plan & wrap (20s)

**Switch to 🤖 AI Plan tab, click "Generate plan for today".**

> "Cerebras Llama takes the joined view and plans my day in 30-60 minute blocks, sorted by urgency. That's the full loop: file → Coral SQL → AI plan, end to end."

**Final shot:** GitHub repo URL on screen:
> "Code is at github.com/Tanya-garg10/Coral-Compass. Thanks!"

---

## 🎤 Talking points if a judge asks

- **Why Coral over plain SQLite?** Coral's source spec model is portable: same join works on live APIs (GitHub, Linear, Notion) without rewriting the SQL or building tool wrappers.
- **What about Windows?** Native binary; install script in the repo.
- **What's the fallback for?** Cloud deployments (Streamlit Cloud) can't install the Coral CLI, so DuckDB keeps the demo working anywhere.
- **What's next?** Plug in Google Calendar + Notion via Coral specs, add reminders, and expose the runtime over MCP so any agent can query it.

---

## ✅ Pre-recording checklist

- [ ] `coral source list` shows `studysync` with 2 tables
- [ ] `coral sql ...` runs and prints the 5-row table
- [ ] Streamlit sidebar shows **Coral CLI: detected ✅** and **Cerebras detected**
- [ ] AI Plan tab actually generates output (not the rule-based fallback)
- [ ] Browser zoom at 100–110% so text is sharp on recording
- [ ] Terminal font size bumped up
