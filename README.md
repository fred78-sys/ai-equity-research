# AI Equity Research Model — v0.1

A low-cost US-equity research prototype that creates a ranked report, Streamlit dashboard, and transparent historical backtest.

**Scope and safety**
- Research only: no broker connection, order routing, or live execution.
- The ranking is a price-only baseline, not a complete fundamental or AI model.
- Educational software, not investment advice. Historical performance does not guarantee future results.
- `yfinance` is for prototyping; review Yahoo/yfinance terms and data rights before commercial use.
- Historical universe survivorship bias, point-in-time data, delistings, and corporate actions need further work before investment use.

## Install

Python 3.11 recommended (3.10+ should work).

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
python -m src.main
```

Creates `outputs/latest_ranking.csv`, `outputs/latest_ranking.html`, `outputs/backtest.csv`, `outputs/performance_summary.yaml`, and `outputs/prices_snapshot.parquet`.

Then launch the dashboard:

```bash
streamlit run app.py
```

Run tests with `pytest -q`.

The default tickers are a **smoke-test universe only**. Edit `config/settings.yaml` before use and retain `SPY` as benchmark.

## Model formulas

- 12–1 momentum = adjusted close at t−21 sessions / adjusted close at t−252 sessions − 1.
- 63-day annualized volatility = standard deviation of daily returns over trailing 63 sessions × √252.
- Momentum score = cross-sectional percentile rank × 100.
- Low-volatility score = 100 − cross-sectional volatility percentile rank × 100.
- Composite score = 0.75 × momentum score + 0.25 × low-volatility score.

The strategy rebalances monthly. It applies prior-session weights to current-session returns to avoid using a close and its resulting return on the same day. The transaction cost is only a configurable assumption, not a market-impact model.

## Limitations

1. The price source is a third-party wrapper; availability and data terms can change.
2. The universe is not point-in-time and has survivorship/selection bias.
3. A monthly portfolio backtest is not the same as evaluating a 6-month forecast. Add forward 126-session returns and rank-IC evaluation before making predictive claims.
4. Sharpe uses a zero risk-free rate; annualized statistics can be unstable on short samples.
5. No portfolio constraints, sector neutrality, liquidity filters, taxes, borrow fees, calibrated slippage, or corporate-action audit.
6. Inspect missing/stale prices and data quality before trusting results.
7. Do not use outputs as a standalone investment decision.

## Upgrade path

1. Add data-quality checks and reproducible snapshots.
2. Expand to a documented US universe and explicitly measure survivorship bias.
3. Add point-in-time fundamentals from a licensed vendor or SEC filings.
4. Add forward 126-session labels, rank IC, walk-forward validation, and sector-aware tests.
5. Add cost/turnover sensitivity, risk constraints, experiment tracking, and monitoring.
6. Any execution integration requires separate legal, data-rights, risk, and engineering reviews. Execution is intentionally out of scope for v0.1.
