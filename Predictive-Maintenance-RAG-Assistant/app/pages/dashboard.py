import sys
from pathlib import Path
from dataclasses import asdict

import altair as alt
import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database import get_conversations, get_statistic

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
