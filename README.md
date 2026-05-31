# 🪸 Coral Compass — StudySync AI

Smart study planner that **SQL-joins your assignments with your notes** and generates an AI-powered study plan for today.

Built with Python, Streamlit, Pandas, OpenAI, and **[Coral](https://withcoral.com)** — one SQL interface over local files. A DuckDB engine is bundled as a fallback so the app works even before Coral is installed.

## ✨ Features

- Dashboard of all assignments and notes
- **Real SQL** join over CSV file sources via Coral CLI (or DuckDB fallback)
- Auto-calculates days remaining and priority (Urgent / High / Medium / Low)
- AI-generated study plan for today via OpenAI, with rule-based fallback
- Filter by subject and deadline window

## 🗂 Project structure

```
Coral-Compass/
├── app.py                 # Streamlit app (Coral + DuckDB SQL, AI plan)
├── assignments.csv        # Assignments data source
├── notes.csv              # Notes data source
├── studysync.coral.yaml   # Coral source spec (file backend)
├── requirements.txt
├── install_coral.ps1      # Windows installer for Coral CLI
├── coral_setup.ps1        # Lints + adds the source, runs sample query
├── .env.example           # OPENAI_API_KEY placeholder
└── .gitignore
```

## 🚀 Quick start

### 1. Install Python dependencies

```bash
git clone https://github.com/Tanya-garg10/Coral-Compass.git
cd Coral-Compass
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Install the Coral CLI (recommended)

**Windows (PowerShell):**
```powershell
.\install_coral.ps1
```
This downloads the official `coral-x86_64-pc-windows-msvc.zip`, extracts `coral.exe` to `%USERPROFILE%\.local\bin`, and adds it to your user PATH.

**macOS / Linux:**
```bash
brew install withcoral/tap/coral
# or
curl -fsSL https://withcoral.com/install.sh | sh
```

Verify:
```bash
coral --version
```

### 3. Register the CSV file source in Coral

```powershell
.\coral_setup.ps1
```
This:
- lints `studysync.coral.yaml`
- runs `coral source add --file studysync.coral.yaml`
- runs a sample joined SQL query and prints the result

> Note: `studysync.coral.yaml` uses absolute `file://` locations for the CSVs. If you clone this repo into a different path, update the `location:` fields in the YAML to match your local path.

### 4. (Optional) Add an OpenAI key for the AI plan

```bash
copy .env.example .env       # Windows
# or: cp .env.example .env
# then edit .env and set OPENAI_API_KEY=sk-...
```
Without a key, a rule-based plan is shown automatically.

### 5. Run the app

```bash
streamlit run app.py
```
Open the URL Streamlit prints (usually http://localhost:8501).

The app auto-detects whether `coral` is on PATH. The **Coral SQL** tab lets you run queries through Coral live, or through DuckDB as a fallback.

## 🔗 The join (Coral SQL)

```sql
SELECT a.subject, a.assignment, a.deadline, n.note_topic
FROM studysync.assignments a
JOIN studysync.notes n ON a.subject = n.subject
ORDER BY a.deadline;
```

CLI:
```bash
coral sql "SELECT a.subject, a.assignment, a.deadline, n.note_topic
           FROM studysync.assignments a
           JOIN studysync.notes n ON a.subject = n.subject
           ORDER BY a.deadline"
```

Sample output:
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

Take a screenshot of this output for your submission.

## 🧱 Architecture

```
CSV / file sources  ──▶  Coral (SQL over files)  ──▶  Streamlit UI  ──▶  OpenAI (study plan)
                          │
                          └── fallback: DuckDB (in-process)
```

## 🚧 Future improvements

- **Live data sources** — replace CSVs with Google Calendar, Notion, and Google Drive via Coral source specs so assignments and notes sync automatically.
- **Smart reminders** — email / Slack / Discord notifications for upcoming deadlines, generated from the same SQL view.
- **Per-user accounts** — auth + per-student data so the app works for a class, not just one user.
- **Study session tracking** — log time spent per topic and feed it back into the AI plan to recommend weaker areas.
- **Pomodoro mode** — built-in 25/5 timer linked to each generated study block.
- **Spaced repetition** — flashcards generated from notes, scheduled with an SM-2 style algorithm.
- **Calendar export** — one-click export of today's plan as `.ics` so it lands on any calendar app.
- **Mobile-friendly UI** — responsive layout and PWA install for on-the-go use.
- **Coral MCP integration** — expose the same SQL runtime to Claude / Cursor / Kiro via `coral mcp` so an agent can plan and reschedule for you.
- **Multi-user deployment** — Dockerfile + Postgres-backed catalog for hosted use.

Made with 🪸 and ❤️ by [Tanya Garg](https://github.com/Tanya-garg10).
