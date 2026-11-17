CREATE TABLE IF NOT EXISTS markets (
    ticker TEXT PRIMARY KEY,
    series_ticker TEXT NOT NULL,
    open_time TEXT,
    close_time TEXT NOT NULL,
    settlement_ts TEXT,
    status TEXT,
    result TEXT,
    source TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    raw_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS markets_close_time ON markets(close_time);

CREATE TABLE IF NOT EXISTS trades (
    trade_id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL,
    created_time TEXT,
    yes_price_dollars TEXT,
    no_price_dollars TEXT,
    count_fp TEXT,
    source TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS trades_ticker ON trades(ticker);

CREATE TABLE IF NOT EXISTS trade_summary (
    ticker TEXT NOT NULL,
    minute_utc TEXT NOT NULL,
    yes_price_cent INTEGER NOT NULL,
    trade_count INTEGER NOT NULL,
    contracts TEXT NOT NULL,
    PRIMARY KEY (ticker, minute_utc, yes_price_cent)
);

CREATE TABLE IF NOT EXISTS candles (
    ticker TEXT NOT NULL,
    end_period_ts INTEGER NOT NULL,
    end_time TEXT NOT NULL,
    yes_bid_close TEXT,
    yes_ask_close TEXT,
    price_close TEXT,
    volume_fp TEXT,
    source TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    PRIMARY KEY (ticker, end_period_ts)
);

CREATE TABLE IF NOT EXISTS completed (
    kind TEXT NOT NULL,
    ticker TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    PRIMARY KEY (kind, ticker)
);
