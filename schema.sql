-- Research storage proposal. The starter collector currently writes JSONL only.
CREATE TABLE IF NOT EXISTS markets (
  ticker TEXT PRIMARY KEY, series_ticker TEXT NOT NULL,
  open_time_utc TEXT, close_time_utc TEXT,
  official_result TEXT, observed_at_utc TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS trade_candidates (
  trade_id TEXT PRIMARY KEY, ticker TEXT NOT NULL,
  side TEXT NOT NULL CHECK(side IN ('yes','no')),
  price_dollars TEXT NOT NULL, quantity TEXT,
  executed_at_utc TEXT, FOREIGN KEY(ticker) REFERENCES markets(ticker)
);
CREATE TABLE IF NOT EXISTS book_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL,
  captured_at_utc TEXT NOT NULL, raw_json TEXT NOT NULL
);
