# Data schema and provenance

`schema.sql` defines the compact SQLite tables. `markets` and `candles` retain raw API records. `trades` contains individual public non-block trades priced from 1–5¢ inclusive on either YES or NO, without redundant raw JSON. `trade_summary` counts all other trades and sums contract volume by market, UTC minute, and one-cent YES price bucket. `completed` records fully downloaded trade and candle datasets by market ticker so interrupted runs can resume.

The collector selects markets by UTC close date. Prices remain decimal strings as returned by the API.

`trades` are observed public non-block trades, not hypothetical fills. One-minute `candles` are Kalshi market price and quote aggregates, not order-book history.
