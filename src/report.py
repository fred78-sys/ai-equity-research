from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def export_ranking(ranking: pd.DataFrame) -> None:
    ranking.to_csv(OUTPUT_DIR / "latest_ranking.csv", index_label="ticker")
    ranking.to_html(OUTPUT_DIR / "latest_ranking.html", index=True, border=0,
                    float_format=lambda value: f"{value:.3f}")


def performance_summary(backtest: pd.DataFrame) -> dict[str, float | int]:
    returns = backtest["strategy_return"].dropna()
    if len(returns) < 2:
        raise ValueError("Insufficient returns to evaluate.")
    equity = (1.0 + returns).cumprod()
    years = len(returns) / 252.0
    annualized_return = equity.iloc[-1] ** (1.0 / years) - 1.0 if years > 0 and equity.iloc[-1] > 0 else float("nan")
    annualized_volatility = returns.std(ddof=1) * (252.0 ** 0.5)
    sharpe = returns.mean() / returns.std(ddof=1) * (252.0 ** 0.5) if returns.std(ddof=1) > 0 else float("nan")
    drawdown = equity / equity.cummax() - 1.0
    return {
        "annualized_return": float(annualized_return),
        "annualized_volatility": float(annualized_volatility),
        "sharpe_zero_rf": float(sharpe),
        "maximum_drawdown": float(drawdown.min()),
        "observations": int(len(returns)),
    }
