from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

OUTPUTS = Path(__file__).resolve().parent / "outputs"
st.set_page_config(page_title="AI Equity Research v0.1", layout="wide")
st.title("US Equity Research — v0.1")
st.caption("Price-only research prototype. Not investment advice. No live order execution or broker connection.")

ranking_path = OUTPUTS / "latest_ranking.csv"
backtest_path = OUTPUTS / "backtest.csv"
if not ranking_path.exists():
    st.warning("No ranking found. Run `python -m src.main` from the project root first.")
    st.stop()

ranking = pd.read_csv(ranking_path)
if "ticker" not in ranking.columns:
    ranking = ranking.rename(columns={ranking.columns[0]: "ticker"})

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Latest ranked universe")
    st.dataframe(ranking, use_container_width=True, hide_index=True)
    st.download_button("Download ranking CSV", data=ranking.to_csv(index=False).encode("utf-8"),
                       file_name="latest_ranking.csv", mime="text/csv")
with right:
    st.subheader("Factor scores")
    if {"ticker", "momentum_score", "risk_score"}.issubset(ranking.columns):
        selected = st.selectbox("Select ticker", ranking["ticker"].astype(str).tolist())
        row = ranking.loc[ranking["ticker"].astype(str) == selected].iloc[0]
        scores = pd.DataFrame({"Factor": ["12–1 momentum", "Low volatility"],
                               "Score": [row["momentum_score"], row["risk_score"]]})
        st.metric("Composite score", f"{row['score']:.1f}/100")
        st.plotly_chart(px.bar(scores, x="Factor", y="Score", range_y=[0, 100],
                                title=f"{selected} factor scores"), use_container_width=True)
    else:
        st.info("Factor score columns are not available.")

st.divider()
st.subheader("Historical backtest")
if backtest_path.exists():
    backtest = pd.read_csv(backtest_path, parse_dates=["date"])
    if {"date", "strategy_equity", "benchmark_equity"}.issubset(backtest.columns):
        long = backtest.melt(id_vars="date", value_vars=["strategy_equity", "benchmark_equity"],
                             var_name="Series", value_name="Growth of $1")
        st.plotly_chart(px.line(long, x="date", y="Growth of $1", color="Series"),
                        use_container_width=True)
        st.download_button("Download backtest CSV", data=backtest.to_csv(index=False).encode("utf-8"),
                           file_name="backtest.csv", mime="text/csv")
    else:
        st.warning("Backtest file exists but expected columns are missing.")
else:
    st.info("Run the pipeline to create the backtest file.")
