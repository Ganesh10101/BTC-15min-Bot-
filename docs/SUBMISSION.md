# Week 1 submission and reproducibility

**Source:** Group 2 slides and Nov 13 research documentation. This is a new independent starter implementation, not a copy of the prior team's code.

## Local commands

```bash
python -m unittest discover -s tests -v
python demo_fixture.py
python analyze.py --csv examples/synthetic/candidate_trades.csv --out analysis
python collector.py --once --data-dir data
```

The first three commands use local synthetic data and no credentials. The last command attempts public live **GET** requests and may fail due to network access, API changes or rate limits. It does not backfill 30 days, store SQLite records or place orders.

## Research deliverables still outstanding

- At least 30 days of real market/trade/outcome coverage and explicit missing-data report
- Validated historical API pagination and archive handling
- SQL normalization and candidate trade extraction
- Statistical comparisons of cooldown windows using non-lookahead labels
- Queue-aware, fee-aware execution simulation and cancellation-latency analysis
