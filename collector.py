"""Read-only public Kalshi API snapshot collector (not historical backfill)."""
import argparse
import datetime as dt
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://external-api.kalshi.com/trade-api/v2"

def fetch(path, params=None):
    """Fetch one public GET endpoint; return an auditable response envelope."""
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    requested = dt.datetime.now(dt.timezone.utc).isoformat()
    start = time.monotonic()
    envelope = {"requested_at_utc": requested, "method": "GET", "url": url,
                "status": None, "payload": None, "error": None}
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent":"KXBTC15M-research/0.1"})
        with urllib.request.urlopen(req, timeout=20) as response:
            envelope["status"] = response.status
            envelope["payload"] = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        envelope["error"] = str(exc)
    envelope["captured_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    envelope["latency_ms"] = round((time.monotonic()-start)*1000, 1)
    return envelope

def snapshot(data_dir):
    """Collect current series and open-market snapshots; no order endpoints."""
    output = Path(data_dir)
    output.mkdir(parents=True, exist_ok=True)
    records = [fetch('/series/KXBTC15M'), fetch('/markets',
               {'series_ticker':'KXBTC15M','status':'open','limit':100})]
    markets = records[1].get('payload') or {}
    for market in markets.get('markets', []):
        ticker = market.get('ticker')
        if ticker:
            records.append(fetch('/markets/'+urllib.parse.quote(ticker,safe='')+'/orderbook'))
            records.append(fetch('/markets/trades', {'ticker':ticker,'limit':1000,'is_block_trade':'false'}))
    with (output/'raw_responses.jsonl').open('a',encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record,ensure_ascii=False)+'\n')
    return len(records)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Read-only Kalshi market snapshot collector')
    parser.add_argument('--once',action='store_true')
    parser.add_argument('--interval',type=float,default=0)
    parser.add_argument('--data-dir',default='data')
    args=parser.parse_args()
    if not args.once and args.interval<=0:
        parser.error('Use --once or a positive --interval in seconds')
    while True:
        print('Saved',snapshot(args.data_dir),'GET response envelopes')
        if args.once:break
        time.sleep(args.interval)
