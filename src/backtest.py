import pandas as pd

from src.scoring import rank_stocks


def run_backtest(prices: pd.DataFrame, features: dict[str, pd.DataFrame], benchmark: str = "SPY",
                 top_n: int = 10, transaction_cost_bps: float = 5.0) -> pd.DataFrame:
    """Simple monthly equal-weight top-N backtest; research prototype only."""
    if benchmark not in prices.columns:
        raise ValueError(f"Missing benchmark: {benchmark}")
    if top_n < 1:
        raise ValueError("top_n must be at least 1.")
    if transaction_cost_bps < 0:
        raise ValueError("transaction_cost_bps cannot be negative.")
    prices = prices.sort_index()
    returns = prices.pct_change(fill_method=None)
    dates = prices.index
    month_ends = pd.Series(dates, index=dates).groupby(dates.to_period("M")).last().tolist()
    targets = pd.DataFrame(float("nan"), index=dates, columns=prices.columns)
    for date in month_ends:
        if dates.get_loc(date) + 1 >= len(dates):
            continue
        try:
            ranking = rank_stocks(features, as_of=date, min_history_days=252)
        except ValueError:
            continue
        selected = [t for t in ranking.index if t != benchmark and t in prices.columns][:top_n]
        if not selected:
            continue
        target = pd.Series(0.0, index=prices.columns)
        target.loc[selected] = 1.0 / len(selected)
        targets.loc[date] = target
    targets = targets.ffill().fillna(0.0)
    held_weights = targets.shift(1).fillna(0.0)
    gross = (held_weights * returns.fillna(0.0)).sum(axis=1)
    turnover = targets.diff().abs().sum(axis=1)
    if len(turnover):
        first_invested = targets.ne(0).any(axis=1)
        if first_invested.any():
            first_date = first_invested[first_invested].index[0]
            turnover.loc[first_date] = targets.loc[first_date].abs().sum()
    costs = turnover * transaction_cost_bps / 10_000.0
    net = gross - costs
    result = pd.DataFrame({
        "strategy_return": net,
        "gross_return": gross,
        "transaction_cost": costs,
        "turnover": turnover,
        "benchmark_return": returns[benchmark].fillna(0.0),
    }, index=dates)
    result["strategy_equity"] = (1.0 + result["strategy_return"]).cumprod()
    result["benchmark_equity"] = (1.0 + result["benchmark_return"]).cumprod()
    return result
