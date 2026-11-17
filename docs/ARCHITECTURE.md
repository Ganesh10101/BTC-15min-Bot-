# Architecture

```mermaid
flowchart TD
 A[Kalshi public REST API] --> B[collector.py]
 B --> C[SQLite: markets, candles, extreme trades, other-trade summaries]
 C --> D[analyze.py: observed 1-cent trades]
 D --> E[Future fill-aware paper testing]
```

**Implemented:** read-only backfill by UTC market close date, archive cutoff handling, pagination, retries, SQLite storage with resumable per-market trade/candle downloads, and descriptive 1-cent trade analysis.

**Planned:** live order-book capture, execution-aware simulations, and out-of-sample validation.
