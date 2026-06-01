"""
StudySync AI - Smart study planner that joins assignments with notes
and generates an AI-powered study plan.

Data layer: SQL over CSV file sources.
- If the Coral CLI (https://withcoral.com) is installed and on PATH,
  the "Coral SQL" tab runs the query through `coral sql`.
- Otherwise it falls back to an in-process DuckDB engine that reads
  the same CSVs with identical SQL semantics.
"""

import os
import shutil
import subprocess
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="StudySync AI", page_icon="📚", layout="wide")

ROOT = Path(__file__).parent
ASSIGNMENTS_CSV = ROOT / "assignments.csv"
NOTES_CSV = ROOT / "notes.csv"

JOIN_SQL = """
SELECT a.subject, a.assignment, a.deadline, n.note_topic
FROM assignments a
JOIN notes n ON a.subject = n.subject
ORDER BY a.deadline
""".strip()


# ---------- Data helpers ----------
@st.cache_data
def load_csvs():
    assignments = pd.read_csv(ASSIGNMENTS_CSV)
    notes = pd.read_csv(NOTES_CSV)
    assignments["deadline"] = pd.to_datetime(assignments["deadline"]).dt.date
    return assignments, notes


def days_left(d) -> int:
    # `d` may be a datetime.date, datetime.datetime, or pandas.Timestamp
    # depending on the SQL backend. Normalize to date.
    if hasattr(d, "date"):
        d = d.date()
    return (d - date.today()).days


def priority(days: int) -> str:
    if days <= 1:
        return "🔴 Urgent"
    if days <= 3:
        return "🟠 High"
    if days <= 6:
        return "🟡 Medium"
    return "🟢 Low"


# ---------- SQL backends ----------
def _coral_path():
    """Locate the coral CLI.
    Priority:
    1. CORAL_PATH env var (explicit override, most reliable)
    2. shutil.which (PATH-based)
    3. ~/.local/bin/coral.exe (Windows default install location)
    """
    # 1. Explicit env override
    env_path = os.getenv("CORAL_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    # 2. PATH-based
    p = shutil.which("coral") or shutil.which("coral.exe")
    if p:
        return p

    # 3. Default Windows install location
    candidates = [
        Path.home() / ".local" / "bin" / "coral.exe",
        Path.home() / ".local" / "bin" / "coral",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def coral_available() -> bool:
    return _coral_path() is not None


def run_duckdb(sql: str) -> pd.DataFrame:
    con = duckdb.connect(":memory:")
    con.execute(
        f"CREATE VIEW assignments AS SELECT * FROM read_csv_auto('{ASSIGNMENTS_CSV.as_posix()}')"
    )
    con.execute(
        f"CREATE VIEW notes AS SELECT * FROM read_csv_auto('{NOTES_CSV.as_posix()}')"
    )
    return con.execute(sql).fetch_df()


def run_coral(sql: str) -> tuple[str, str]:
    """Run a query through the Coral CLI. Returns (stdout, stderr)."""
    coral = _coral_path() or "coral"
    proc = subprocess.run(
        [coral, "sql", sql],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.stdout, proc.stderr


# ---------- AI study plan ----------
def generate_ai_plan(merged: pd.DataFrame) -> str:
    """Build today's study plan via an OpenAI-compatible chat API.

    Supports any provider that exposes the OpenAI chat-completions schema:
    OpenAI, Cerebras, OpenRouter, Groq, Together, etc. Configure via env:

        AI_API_KEY=...                 # required
        AI_BASE_URL=...                # optional (defaults to provider-specific)
        AI_MODEL=...                   # optional (defaults to provider-specific)

    For backwards compatibility we also read OPENAI_API_KEY,
    CEREBRAS_API_KEY, and OPENROUTER_API_KEY.
    """
    # Pick the first key that is set, and a sensible default base_url+model
    # for that provider.
    if os.getenv("CEREBRAS_API_KEY"):
        api_key = os.getenv("CEREBRAS_API_KEY")
        base_url = os.getenv("AI_BASE_URL", "https://api.cerebras.ai/v1")
        model = os.getenv("AI_MODEL", "gpt-oss-120b")
    elif os.getenv("OPENROUTER_API_KEY"):
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1")
        model = os.getenv("AI_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
    elif os.getenv("OPENAI_API_KEY"):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("AI_BASE_URL")  # SDK default
        model = os.getenv("AI_MODEL", "gpt-4o-mini")
    elif os.getenv("AI_API_KEY"):
        api_key = os.getenv("AI_API_KEY")
        base_url = os.getenv("AI_BASE_URL")
        model = os.getenv("AI_MODEL", "gpt-4o-mini")
    else:
        return _fallback_plan(merged)

    try:
        from openai import OpenAI

        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        client = OpenAI(**kwargs)

        rows = "\n".join(
            f"- {r.subject}: {r.assignment} (due {r.deadline}, "
            f"topic: {r.note_topic}, {r.days_left} days left)"
            for r in merged.itertuples()
        )
        prompt = (
            "You are a focused study planner. Based on the assignments below, "
            "create a prioritized study plan for TODAY only. Use bullet points, "
            "suggest 30-60 min time blocks, and prioritize by deadline urgency.\n\n"
            f"Assignments:\n{rows}\n"
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return resp.choices[0].message.content
    except Exception as e:  # noqa: BLE001
        return f"_AI unavailable ({e}). Showing rule-based plan._\n\n" + _fallback_plan(
            merged
        )


def _fallback_plan(merged: pd.DataFrame) -> str:
    sorted_df = merged.sort_values("days_left")
    lines = ["### Today's Study Plan", ""]
    for r in sorted_df.itertuples():
        lines.append(
            f"- **45 min** — Study *{r.note_topic}* for **{r.assignment}** "
            f"({r.subject}). Due {r.deadline} ({r.days_left} days left)."
        )
    lines.append("")
    lines.append("Take a 10 min break between blocks. Stay hydrated. 💧")
    return "\n".join(lines)


# ---------- UI ----------
def main():
    st.title("📚 StudySync AI")
    st.caption(
        "Smart study planner — SQL-joins your assignments with your notes "
        "and generates an AI-powered plan."
    )

    assignments, notes = load_csvs()
    merged = run_duckdb(JOIN_SQL)
    merged["days_left"] = merged["deadline"].apply(days_left)
    merged["priority"] = merged["days_left"].apply(priority)
    merged = merged.sort_values("days_left")

    # Sidebar
    st.sidebar.header("Filters")
    subjects = st.sidebar.multiselect(
        "Subjects",
        options=sorted(merged["subject"].unique()),
        default=sorted(merged["subject"].unique()),
    )
    max_days = st.sidebar.slider("Show items due within (days)", 1, 30, 14)
    view = merged[
        (merged["subject"].isin(subjects)) & (merged["days_left"] <= max_days)
    ]

    st.sidebar.divider()
    st.sidebar.subheader("Data layer")
    coral_path = _coral_path()
    if coral_path:
        st.sidebar.success("Coral CLI: detected ✅")
        st.sidebar.caption(f"`{coral_path}`")
    else:
        st.sidebar.info(
            "🪸 Coral SQL (local) · DuckDB (cloud)\n\n"
            "Coral runs locally — see `studysync.coral.yaml` and the demo video for the live integration."
        )

    st.sidebar.subheader("AI provider")
    if os.getenv("CEREBRAS_API_KEY"):
        st.sidebar.success("Cerebras detected")
    elif os.getenv("OPENROUTER_API_KEY"):
        st.sidebar.success("OpenRouter detected")
    elif os.getenv("OPENAI_API_KEY") or os.getenv("AI_API_KEY"):
        st.sidebar.success("OpenAI-compatible key detected")
    else:
        st.sidebar.info("No AI key. Rule-based plan only.")

    # Top metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Assignments", len(view))
    c2.metric("Urgent (≤ 1 day)", int((view["days_left"] <= 1).sum()))
    c3.metric("Next deadline", str(view["deadline"].min() if len(view) else "—"))

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Sources", "🔗 Joined View", "🪸 Coral SQL", "🤖 AI Plan"]
    )

    with tab1:
        st.subheader("assignments.csv")
        st.dataframe(assignments, use_container_width=True)
        st.subheader("notes.csv")
        st.dataframe(notes, use_container_width=True)

    with tab2:
        st.subheader("Joined: Assignments × Notes")
        st.code(JOIN_SQL, language="sql")
        st.dataframe(
            view[
                ["priority", "subject", "assignment", "note_topic", "deadline", "days_left"]
            ],
            use_container_width=True,
        )

    with tab3:
        st.subheader("Run SQL across file sources")
        st.write(
            "If the Coral CLI is installed and the `studysync` source is "
            "configured, this tab runs your query through Coral. Otherwise it "
            "uses an in-process DuckDB engine over the same CSVs."
        )
        default_sql = (
            "SELECT a.subject, a.assignment, a.deadline, n.note_topic\n"
            "FROM assignments a JOIN notes n ON a.subject = n.subject\n"
            "ORDER BY a.deadline"
        )
        sql = st.text_area("SQL", value=default_sql, height=140)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Run with DuckDB"):
                try:
                    df = run_duckdb(sql)
                    st.success(f"{len(df)} rows")
                    st.dataframe(df, use_container_width=True)
                except Exception as e:  # noqa: BLE001
                    st.error(str(e))
        with col2:
            run_coral_btn = st.button(
                "🪸 Run with Coral", disabled=not coral_available()
            )
            if run_coral_btn:
                try:
                    # In Coral, the CSVs are exposed under the `studysync`
                    # schema (see studysync.coral.yaml). Rewrite bare table
                    # refs so the same query in the box works for both
                    # backends.
                    coral_sql = sql
                    for tbl in ("assignments", "notes"):
                        coral_sql = coral_sql.replace(
                            f" {tbl} ", f" studysync.{tbl} "
                        )
                        coral_sql = coral_sql.replace(
                            f"FROM {tbl}", f"FROM studysync.{tbl}"
                        )
                        coral_sql = coral_sql.replace(
                            f"JOIN {tbl}", f"JOIN studysync.{tbl}"
                        )
                    out, err = run_coral(coral_sql)
                    if err:
                        st.warning(err)
                    st.code(out or "(no output)", language="text")
                except FileNotFoundError:
                    st.error("Coral CLI not found on PATH.")
                except subprocess.TimeoutExpired:
                    st.error("Coral query timed out.")

    with tab4:
        st.subheader("AI-generated study plan")
        if st.button("✨ Generate plan for today"):
            with st.spinner("Thinking..."):
                plan = generate_ai_plan(view)
            st.markdown(plan)
        else:
            st.info(
                "Click the button to generate a plan. Set CEREBRAS_API_KEY "
                "(or OPENAI_API_KEY / OPENROUTER_API_KEY) in .env to use AI; "
                "otherwise a rule-based plan is shown."
            )


if __name__ == "__main__":
    main()
