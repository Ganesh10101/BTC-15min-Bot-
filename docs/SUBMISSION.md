# Week 1 submission and reproducibility

**Source:** Group 2 slides and Nov 13 research documentation. This is a new independent starter implementation, not a copy of the prior team's code.

## Local commands

```bash
python3 collector.py
python3 collector.py --start 2026-10-17 --end 2026-11-15
```

The collector uses public read-only **GET** requests, stores results in `data/kalshi_compact.sqlite3`, and requires no API credentials. The default run collects markets closing yesterday in UTC. The second command illustrates a 30-day range. It does not place orders.

## Research deliverables still outstanding

- At least 30 days of real market/trade/outcome coverage and explicit missing-data report
- Longer-period candidate analysis beyond the initial one-day summary
- Statistical comparisons of cooldown windows using non-lookahead labels
- Queue-aware, fee-aware execution simulation and cancellation-latency analysis
