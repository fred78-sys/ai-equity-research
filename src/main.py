from pathlib import Path

import pandas as pd
import yaml

from src.backtest import run_backtest
from src.data import download_prices
from src.features import calculate_features
from src.report import export_ranking, performance_summary
from src.scoring import rank_stocks

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)


def main() -> None:
    with (ROOT / "config" / "settings.yaml").open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    prices = download_prices(config["universe"]["tickers"], start=config["data"]["start_date"])
    prices.to_parquet(OUTPUTS / "prices_snapshot.parquet")
    benchmark = config["data"]["benchmark"]
    if benchmark not in prices.columns:
        raise RuntimeError(f"Benchmark {benchmark!r} missing from downloaded data.")
    features = calculate_features(prices)
    ranking = rank_stocks(features, min_history_days=int(config["model"].get("min_history_days", 252)))
    export_ranking(ranking)
    backtest = run_backtest(
        prices, features, benchmark=benchmark,
        top_n=int(config["model"]["top_n"]),
        transaction_cost_bps=float(config["backtest"]["transaction_cost_bps"]),
    )
    backtest.to_csv(OUTPUTS / "backtest.csv", index_label="date")
    summary = performance_summary(backtest)
    with (OUTPUTS / "performance_summary.yaml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump(summary, handle, sort_keys=False)
    print("\nLatest ranking:")
    print(ranking.head(10).to_string())
    print("\nBacktest summary (illustrative, not predictive):")
    print(pd.Series(summary).to_string())
    print(f"\nFiles written to: {OUTPUTS.resolve()}")


if __name__ == "__main__":
    main()
