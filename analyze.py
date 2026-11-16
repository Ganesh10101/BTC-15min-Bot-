"""Descriptive analysis of candidate rows, NOT a fill-accurate backtest."""
import argparse
import csv
import json
import math
from pathlib import Path

def wilson_interval(wins, n, z=1.959963984540054):
    if not n:return [None,None]
    p=wins/n
    denom=1+z*z/n
    center=(p+z*z/(2*n))/denom
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return [round(center-half,6),round(center+half,6)]

def analyze(csv_path):
    """Input rows: ticker,side,price_dollars,official_result; one row per candidate trade."""
    with open(csv_path,newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    required={'ticker','side','price_dollars','official_result'}
    if rows and not required.issubset(rows[0]):
        raise ValueError('Missing columns: '+', '.join(sorted(required-set(rows[0]))))
    eligible=[r for r in rows if r['price_dollars'].strip() in ('0.01','0.0100')
              and r['side'].lower() in ('yes','no')
              and r['official_result'].lower() in ('yes','no')]
    wins=sum(r['side'].lower()==r['official_result'].lower() for r in eligible)
    n=len(eligible)
    return {'candidate_trades':n,'candidate_wins':wins,
            'candidate_win_rate':wins/n if n else None,
            'wilson_95':wilson_interval(wins,n),
            'warning':'Public trade candidates are not hypothetical strategy fills.'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--csv',required=True,help='CSV of settled 1-cent public trade candidates')
    p.add_argument('--out',default='analysis')
    a=p.parse_args()
    result=analyze(a.csv)
    Path(a.out).mkdir(parents=True,exist_ok=True)
    (Path(a.out)/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
