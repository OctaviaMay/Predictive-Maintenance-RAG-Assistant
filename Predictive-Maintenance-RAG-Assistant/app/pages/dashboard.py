import sys
from pathlib import Path
from dataclasses import asdict

import altair as alt
import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database import get_conversations, get_statistic, get_groundedness_stats

# --- Palette --------------------------------------------------------------
PRIMARY = "#2a78d6"
ACCENT = "#1baf7a"

st.set_page_config(page_title="Feedback Dashboard", page_icon="📊", layout="wide")

st.title("📊 Feedback & Monitoring Dashboard")
st.caption(
    "Aggregated across every conversation logged to the assistant's database. "
    "Use this to track question volume, cost, and latency as the assistant is used."
)

if st.button("🔄 Refresh"):
    st.rerun()

try:
    stats = get_statistic()
    records = get_conversations(limit=200)
    groundedness = get_groundedness_stats()
except Exception as e:
    st.error(f"Couldn't reach the database: {e}")
    st.stop()

if not records or stats.total == 0:
    st.info("No conversations logged yet. Go ask the assistant a question on the Chat page, then come back here.")
    st.stop()

df = pd.DataFrame([asdict(r) for r in records])
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total conversations", stats.total)
k2.metric("Avg response time", f"{stats.avg_response_time:.2f}s")
k3.metric("Total cost", f"${stats.total_cost:.4f}")
k4.metric("Avg tokens", f"{stats.avg_tokens:.0f}")

# ---------------------------------------------------------------------------
# Answer quality (LLM-judge groundedness)
# ---------------------------------------------------------------------------
st.subheader("Answer quality: groundedness")
st.caption(
    "Share of answers whose claims are all supported by the retrieved "
    "knowledge-base context, as judged by the LLM judge."
)

GROUNDEDNESS_ORDER = ["GROUNDED", "PARTIALLY_GROUNDED", "NOT_GROUNDED"]
GROUNDEDNESS_COLORS = [ACCENT, "#e0a500", "#d64545"]  # green / amber / red

total_judged = sum(groundedness.values())
if total_judged == 0:
    st.info(
        "No groundedness verdicts yet. Answers logged before the groundedness "
        "check was added have no label. Ask a new question to see one."
    )
else:
    g_df = pd.DataFrame({
        "label": GROUNDEDNESS_ORDER,
        "count": [groundedness.get(label, 0) for label in GROUNDEDNESS_ORDER],
    })
    g_df["share"] = g_df["count"] / total_judged

    q1, q2 = st.columns([1, 2])
    q1.metric(
        "Fully grounded answers",
        f"{g_df.loc[0, 'share']:.0%}",
        help="All factual claims supported by the retrieved context",
    )
    q1.metric("Answers judged", total_judged)

    chart = (
        alt.Chart(g_df)
        .mark_bar(cornerRadius=4)
        .encode(
            x=alt.X("count:Q", title="Answers"),
            y=alt.Y("label:N", sort=GROUNDEDNESS_ORDER, title=None),
            color=alt.Color(
                "label:N",
                scale=alt.Scale(domain=GROUNDEDNESS_ORDER, range=GROUNDEDNESS_COLORS),
                legend=None,
            ),
            tooltip=["label:N", "count:Q", alt.Tooltip("share:Q", format=".0%")],
        )
        .properties(height=160)
    )
    q2.altair_chart(chart, width="stretch")

st.divider()

st.divider()



# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Cost over time")
    chart = (
        alt.Chart(df)
        .mark_line(point=True, strokeWidth=2, color=PRIMARY)
        .encode(
            x=alt.X("timestamp:T", title=None),
            y=alt.Y("cost:Q", title="Cost ($)"),
            tooltip=["timestamp:T", "cost:Q", "question:N"],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, width="stretch")

with right:
    st.subheader("Questions per day")
    st.caption("Usage volume - how many questions the assistant is fielding each day.")
    by_day = df["timestamp"].dt.date.value_counts().sort_index().reset_index()
    by_day.columns = ["date", "count"]
    chart = (
        alt.Chart(by_day)
        .mark_bar(cornerRadius=4, color=PRIMARY)
        .encode(
            x=alt.X("date:T", title=None),
            y=alt.Y("count:Q", title="Questions"),
            tooltip=["date:T", "count:Q"],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, width="stretch")

st.subheader("Response time over time")
chart = (
    alt.Chart(df)
    .mark_line(point=True, strokeWidth=2, color=ACCENT)
    .encode(
        x=alt.X("timestamp:T", title=None),
        y=alt.Y("response_time:Q", title="Response time (s)"),
        tooltip=["timestamp:T", "response_time:Q", "question:N"],
    )
    .properties(height=260)
)
st.altair_chart(chart, width="stretch")

st.subheader("Token usage: prompt vs. completion")
st.caption(
    "Where token spend is going each day - a large prompt share usually means "
    "retrieved context dominates cost, while a large completion share points to answers "
    "running long."
)
token_by_day = (
    df.assign(date=df["timestamp"].dt.date)
    .groupby("date")[["prompt_tokens", "completion_tokens"]]
    .sum()
    .reset_index()
    .melt(id_vars="date", value_vars=["prompt_tokens", "completion_tokens"],
          var_name="token_type", value_name="tokens")
)
token_by_day["token_type"] = token_by_day["token_type"].map({
    "prompt_tokens": "Prompt", "completion_tokens": "Completion",
})
chart = (
    alt.Chart(token_by_day)
    .mark_bar()
    .encode(
        x=alt.X("date:T", title=None),
        y=alt.Y("tokens:Q", title="Tokens", stack="zero"),
        color=alt.Color("token_type:N", scale=alt.Scale(range=[PRIMARY, ACCENT]), title="Token type"),
        tooltip=["date:T", "token_type:N", "tokens:Q"],
    )
    .properties(height=260)
)
st.altair_chart(chart, width="stretch")

st.divider()
st.subheader("Recent conversations")
recent = (
    df[["timestamp", "question", "model", "response_time", "cost"]]
    .sort_values("timestamp", ascending=False)
)
st.dataframe(recent, width="stretch", hide_index=True)
