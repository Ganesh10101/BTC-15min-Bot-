"""Summarize observed 1-cent KXBTC15M trades and their settled outcomes."""

import argparse
import json
import sqlite3
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from statistics import median


ONE_CENT = Decimal("0.01")


def tally():
    return {"trades": 0, "contracts": Decimal(0), "wins": 0,
            "winning_contracts": Decimal(0), "losses": 0, "unknown_results": 0}


def record(stats, contracts, outcome):
    stats["trades"] += 1
    stats["contracts"] += contracts
    if outcome == "win":
        stats["wins"] += 1
        stats["winning_contracts"] += contracts
    elif outcome == "loss":
        stats["losses"] += 1
    else:
        stats["unknown_results"] += 1


def report_stats(stats):
    return {"trades": stats["trades"], "contracts": str(stats["contracts"]),
            "wins": stats["wins"], "losses": stats["losses"],
            "unknown_results": stats["unknown_results"],
            "winning_contracts": str(stats["winning_contracts"]),
            "observed_win_rate": round(stats["wins"] / (stats["wins"] + stats["losses"]), 6)
            if stats["wins"] + stats["losses"] else None}


def timing_bucket(seconds_before_close):
    if 0 <= seconds_before_close < 60:
        return "0-1 minutes before close"
    if 60 <= seconds_before_close < 300:
        return "1-5 minutes before close"
    if 300 <= seconds_before_close < 600:
        return "5-10 minutes before close"
    if 600 <= seconds_before_close <= 900:
        return "10-15 minutes before close"
    return "outside 15-minute window"


def analyze(db):
    markets = db.execute("SELECT ticker FROM markets").fetchall()
    market_count = len(markets)
    if not market_count:
        raise SystemExit("No markets in database")
    for kind in ("trades", "candles"):
        done = db.execute(
            """SELECT COUNT(*) FROM markets m JOIN completed c
               ON c.ticker=m.ticker AND c.kind=?""", (kind,)).fetchone()[0]
        if done != market_count:
            raise SystemExit(f"Incomplete {kind}: {done}/{market_count} markets. Run collector.py again after the current backfill finishes.")

    total = tally()
    sides = {"yes": tally(), "no": tally()}
    timing = {}
    by_close_date = {}
    by_trade_hour_utc = {}
    per_market = Counter()
    side_markets = {"yes": set(), "no": set()}
    winning_markets = {"total": set(), "yes": set(), "no": set()}
    rows = db.execute(
        """SELECT t.ticker, t.created_time, t.yes_price_dollars,
                  t.no_price_dollars, t.count_fp, m.close_time, m.result
           FROM trades t JOIN markets m ON m.ticker=t.ticker
           WHERE CAST(t.yes_price_dollars AS REAL)=0.01
              OR CAST(t.no_price_dollars AS REAL)=0.01""")
    for ticker, created, yes_price, no_price, count, close, result in rows:
        contracts = Decimal(count or "0")
        trade_time = datetime.fromisoformat(created.replace("Z", "+00:00"))
        close_time = datetime.fromisoformat(close.replace("Z", "+00:00"))
        seconds_before_close = (close_time - trade_time).total_seconds()
        bucket = timing_bucket(seconds_before_close)
        for side, price in (("yes", yes_price), ("no", no_price)):
            if price is None or Decimal(price) != ONE_CENT:
                continue
            outcome = "win" if result == side else "loss" if result in ("yes", "no") else "unknown"
            record(total, contracts, outcome)
            record(sides[side], contracts, outcome)
            record(timing.setdefault(bucket, tally()), contracts, outcome)
            record(by_close_date.setdefault(close[:10], tally()), contracts, outcome)
            record(by_trade_hour_utc.setdefault(trade_time.strftime("%H"), tally()), contracts, outcome)
            per_market[ticker] += 1
            side_markets[side].add(ticker)
            if outcome == "win":
                winning_markets["total"].add(ticker)
                winning_markets[side].add(ticker)

    return {
        "note": "Public 1-cent prints are not our fills. Prints in one market share an outcome, so trade-level win rates are not independent probabilities.",
        "markets": market_count,
        "markets_with_one_cent_trades": len(per_market),
        "one_cent_trades_per_market": {
            "mean": round(total["trades"] / market_count, 2),
            "median": median([per_market[ticker] for (ticker,) in markets]),
            "max": max(per_market.values(), default=0),
        },
        "total": {"winning_markets": len(winning_markets["total"]), **report_stats(total)},
        "by_side": {side: {"markets": len(side_markets[side]),
                           "winning_markets": len(winning_markets[side]),
                           **report_stats(stats)}
                    for side, stats in sides.items()},
        "by_minutes_before_close": {key: report_stats(value) for key, value in timing.items()},
        "by_market_close_date_utc": {key: report_stats(value) for key, value in sorted(by_close_date.items())},
        "by_trade_hour_utc": {key: report_stats(value) for key, value in sorted(by_trade_hour_utc.items())},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("data/kalshi_compact.sqlite3"))
    parser.add_argument("--out", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    db = sqlite3.connect(args.db)
    try:
        report = analyze(db)
    finally:
        db.close()
    output = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output)
        print(f"Wrote {args.out}")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
