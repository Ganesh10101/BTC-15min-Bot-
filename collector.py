"""Backfill read-only KXBTC15M data from Kalshi's official API."""

import argparse
import gzip
import json
import logging
import re
import sqlite3
import time
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://external-api.kalshi.com/trade-api/v2"
SERIES = "KXBTC15M"
LOW = Decimal("0.01")
HIGH = Decimal("0.05")
LOG = logging.getLogger("collector")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(value):
    value = re.sub(r"\.(\d+)(?=Z|[+-]\d\d:\d\d|$)",
                   lambda match: "." + match[1][:6].ljust(6, "0"), value)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def utc_text(value):
    return parse_time(value).isoformat(timespec="seconds").replace("+00:00", "Z") if value else None


def get(path, params=None):
    url = API + path + ("?" + urlencode(params) if params else "")
    for attempt in range(5):
        try:
            with urlopen(Request(url, headers={"User-Agent": "KXBTC15M-research-collector/1.0",
                                                "Accept-Encoding": "gzip"}), timeout=30) as response:
                body = response.read()
                if response.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return json.loads(body)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 4:
                raise
            retry_after = error.headers.get("Retry-After")
            delay = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
        except URLError:
            if attempt == 4:
                raise
            delay = 2 ** attempt
        LOG.warning("Retrying %s in %s seconds", url, delay)
        time.sleep(delay)


def pages(path, params, field):
    cursor = None
    seen = set()
    while True:
        query = dict(params)
        if cursor:
            query["cursor"] = cursor
        response = get(path, query)
        yield response[field]
        cursor = response.get("cursor")
        if not cursor:
            break
        if cursor in seen:
            raise RuntimeError(f"Repeated pagination cursor from {path}")
        seen.add(cursor)


def save_market(db, row, source, start, end):
    close = utc_text(row.get("close_time"))
    ticker = row.get("ticker")
    if not close or not start <= close < end or not ticker or not ticker.startswith(SERIES):
        return
    db.execute(
        """INSERT INTO markets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(ticker) DO UPDATE SET
             open_time=excluded.open_time, close_time=excluded.close_time,
             settlement_ts=excluded.settlement_ts, status=excluded.status,
             result=excluded.result, source=excluded.source,
             fetched_at=excluded.fetched_at, raw_json=excluded.raw_json""",
        (ticker, SERIES, utc_text(row.get("open_time")), close,
         utc_text(row.get("settlement_ts")), row.get("status"), row.get("result"),
         source, utc_now(), json.dumps(row, separators=(",", ":"))),
    )


def collect_markets(db, start, end, market_cutoff):
    params = {"series_ticker": SERIES, "min_close_ts": int(parse_time(start).timestamp()) - 1,
              "max_close_ts": int(parse_time(end).timestamp()), "limit": 1000}
    for rows in pages("/markets", params, "markets"):
        for row in rows:
            save_market(db, row, "live", start, end)
        db.commit()
    if start < market_cutoff:
        LOG.info("Scanning historical markets; Kalshi has no archive date filter")
        for rows in pages("/historical/markets", {"series_ticker": SERIES, "limit": 1000}, "markets"):
            for row in rows:
                save_market(db, row, "historical", start, end)
            db.commit()


def complete(db, kind, ticker):
    return db.execute("SELECT 1 FROM completed WHERE kind=? AND ticker=?", (kind, ticker)).fetchone() is not None


def mark_complete(db, kind, ticker):
    db.execute("INSERT OR IGNORE INTO completed VALUES (?, ?, ?)", (kind, ticker, utc_now()))
    db.commit()


def trade_sources(market, trade_cutoff):
    if market["open_time"] and market["open_time"] >= trade_cutoff:
        return ("live",)
    if market["close_time"] < trade_cutoff:
        return ("historical",)
    return ("historical", "live")


def add_trade(db, row, source, summary, seen):
    trade_id = row["trade_id"]
    if trade_id in seen:
        return
    seen.add(trade_id)
    ticker = row["ticker"]
    created = row["created_time"]
    if len(created) != 20 or not created.endswith("Z"):
        created = utc_text(created)
    yes = Decimal(row["yes_price_dollars"])
    no = Decimal(row["no_price_dollars"])
    contracts = Decimal(row["count_fp"])
    if LOW <= yes <= HIGH or LOW <= no <= HIGH:
        db.execute(
            """INSERT INTO trades VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(trade_id) DO UPDATE SET
                 ticker=excluded.ticker, created_time=excluded.created_time,
                 yes_price_dollars=excluded.yes_price_dollars,
                 no_price_dollars=excluded.no_price_dollars,
                 count_fp=excluded.count_fp, source=excluded.source""",
            (trade_id, ticker, created, row["yes_price_dollars"],
             row["no_price_dollars"], row["count_fp"], source),
        )
    else:
        key = (created[:16] + ":00Z", int(yes * 100))
        values = summary.setdefault(key, [0, Decimal(0)])
        values[0] += 1
        values[1] += contracts


def save_trade_summary(db, ticker, summary):
    db.execute("DELETE FROM trade_summary WHERE ticker=?", (ticker,))
    db.executemany(
        "INSERT INTO trade_summary VALUES (?, ?, ?, ?, ?)",
        ((ticker, minute, price, count, str(contracts))
         for (minute, price), (count, contracts) in summary.items()),
    )


def collect_trades(db, market, trade_cutoff):
    ticker = market["ticker"]
    if complete(db, "trades", ticker):
        return
    summary = {}
    seen = set()
    for source in trade_sources(market, trade_cutoff):
        path = "/historical/trades" if source == "historical" else "/markets/trades"
        for rows in pages(path, {"ticker": ticker, "limit": 1000, "is_block_trade": "false"}, "trades"):
            for row in rows:
                if not row.get("trade_id"):
                    raise ValueError(f"Trade without trade_id in {ticker}")
                add_trade(db, row, source, summary, seen)
            db.commit()
    save_trade_summary(db, ticker, summary)
    mark_complete(db, "trades", ticker)


def candle_close(row, field):
    values = row.get(field) or {}
    return values.get("close_dollars", values.get("close"))


def collect_candles(db, market, market_cutoff):
    ticker = market["ticker"]
    if complete(db, "candles", ticker):
        return
    if not market["open_time"]:
        raise ValueError(f"Market {ticker} has no open_time")
    historical = bool(market["settlement_ts"] and market["settlement_ts"] < market_cutoff)
    source = "historical" if historical else "live"
    path = (f"/historical/markets/{ticker}/candlesticks" if historical else
            f"/series/{SERIES}/markets/{ticker}/candlesticks")
    params = {"start_ts": int(parse_time(market["open_time"]).timestamp()),
              "end_ts": int(parse_time(market["close_time"]).timestamp()),
              "period_interval": 1}
    response = get(path, params)
    for row in response["candlesticks"]:
        ts = row["end_period_ts"]
        db.execute(
            """INSERT INTO candles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(ticker, end_period_ts) DO UPDATE SET
                 yes_bid_close=excluded.yes_bid_close,
                 yes_ask_close=excluded.yes_ask_close,
                 price_close=excluded.price_close, volume_fp=excluded.volume_fp,
                 source=excluded.source, fetched_at=excluded.fetched_at,
                 raw_json=excluded.raw_json""",
            (ticker, ts, datetime.fromtimestamp(ts, timezone.utc).isoformat().replace("+00:00", "Z"),
             candle_close(row, "yes_bid"), candle_close(row, "yes_ask"),
             candle_close(row, "price"), row.get("volume_fp", row.get("volume")),
             source, utc_now(), json.dumps(row, separators=(",", ":"))),
        )
    mark_complete(db, "candles", ticker)


def main():
    yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, default=yesterday, help="First UTC close date, YYYY-MM-DD")
    parser.add_argument("--end", type=date.fromisoformat, default=yesterday, help="Last UTC close date, inclusive")
    parser.add_argument("--db", type=Path, default=Path("data/kalshi_compact.sqlite3"))
    args = parser.parse_args()
    if args.start > args.end:
        parser.error("--start must be on or before --end")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    start = datetime.combine(args.start, datetime.min.time(), timezone.utc).isoformat().replace("+00:00", "Z")
    end = datetime.combine(args.end + timedelta(days=1), datetime.min.time(), timezone.utc).isoformat().replace("+00:00", "Z")
    args.db.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(args.db)
    db.row_factory = sqlite3.Row
    try:
        old_trades = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='trades'").fetchone()
        if old_trades and "raw_json" in old_trades[0]:
            raise SystemExit(f"{args.db} uses the old full-trade schema; choose a new --db path")
        db.executescript(Path(__file__).with_name("schema.sql").read_text())
        cutoff = get("/historical/cutoff")
        market_cutoff = utc_text(cutoff["market_settled_ts"])
        trade_cutoff = utc_text(cutoff["trades_created_ts"])
        LOG.info("Collecting markets closing %s through %s UTC", args.start, args.end)
        collect_markets(db, start, end, market_cutoff)
        markets = db.execute("SELECT * FROM markets WHERE close_time >= ? AND close_time < ? ORDER BY close_time", (start, end)).fetchall()
        LOG.info("Found %s markets", len(markets))
        for index, market in enumerate(markets, 1):
            collect_trades(db, market, trade_cutoff)
            collect_candles(db, market, market_cutoff)
            if index % 10 == 0 or index == len(markets):
                LOG.info("Processed %s/%s markets", index, len(markets))
        counts = {name: db.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                  for name in ("markets", "trades", "trade_summary", "candles")}
        LOG.info("Database %s: %s", args.db, counts)
    finally:
        db.close()


if __name__ == "__main__":
    main()
