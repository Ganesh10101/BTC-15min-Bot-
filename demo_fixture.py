"""Generate clearly synthetic candidate trades for smoke tests."""
import csv
from pathlib import Path

def generate(path='examples/synthetic/candidate_trades.csv'):
    dest=Path(path)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['ticker','side','price_dollars','official_result'])
        writer.writeheader()
        for i in range(120):
            writer.writerow({'ticker':f'SYNTHETIC-{i:03}', 'side':'yes',
                             'price_dollars':'0.01', 'official_result':'yes' if i in (29,99) else 'no'})
    print('SYNTHETIC example written to',dest)

if __name__=='__main__':generate()
