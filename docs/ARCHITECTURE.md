# Architecture

```mermaid
flowchart TD
 A[Kalshi public API GET] --> B[collector.py]
 B --> C[Append-only raw JSONL]
 C --> D[Future validation and normalization]
 D --> E[SQLite / CSV]
 E --> F[Observed 1-cent trade candidate analysis]
 F --> G[Confidence intervals and cooldown research]
 G --> H[Future fill-aware paper testing]
```

**Implemented:** read-only snapshot collection to JSONL, synthetic data generator, CSV candidate summary, and toy assumed-fill backtester.

**Planned:** historical backfill, SQLite ingestion, execution-aware dual-side order simulations, cancellation latency, out-of-sample validation.
