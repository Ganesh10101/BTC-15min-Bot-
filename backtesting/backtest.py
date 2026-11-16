"""Run a toy backtest with assumed fills on synthetic/labeled CSV rows."""
import argparse
import csv
from strategy.one_cent_strategy import signals
from backtesting.performance import summarize


def run(path: str, cooldown: int = 50) -> dict:
    with open(path, newline='', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise ValueError('CSV has no rows')
    required = {'market_id', 'interval_index', 'reversal', 'yes_settled'}
    if not required.issubset(rows[0]):
        raise ValueError(f'Missing columns: {sorted(required - set(rows[0]))}')
    selected = signals(rows, cooldown=cooldown)
    return summarize(selected)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True)
    parser.add_argument('--cooldown', type=int, default=50)
    args = parser.parse_args()
    print('SYNTHETIC/RESEARCH ONLY — all eligible orders assumed filled')
    for key, value in run(args.csv, args.cooldown).items():
        print(f'{key}: {value}')
