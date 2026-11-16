# Team workflow

- **Data:** Implement historical market collection and schema validation.
- **Research:** Define reversal labels and statistical tests.
- **Strategy:** Implement side selection, cooldown experiments, and entry criteria.
- **Backtesting:** Add quote-based fill simulation, fees, and risk reporting.
- **QA:** Review look-ahead bias, test coverage, and reproducibility.

Use one feature branch per task, include a concise PR description, and run `python -m unittest discover -s tests -v` before merging. Never commit API credentials or private keys.
