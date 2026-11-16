# Data schema and provenance

`schema.sql` is a **proposed normalization schema**. It is not yet populated by `collector.py`.

The current collector appends raw GET response envelopes to `data/raw_responses.jsonl`. Each envelope records URL, HTTP status, UTC request/capture timestamps, latency, error and decoded payload. Responses may contain sensitive data in other contexts; inspect before sharing.

`trade_candidates` represents **observed public trades**, not hypothetical fills. Never treat them as execution evidence. Preserve source timestamps, decimal strings, and official settlement results. The schema and parsing must be validated against live API responses before database ingestion.
