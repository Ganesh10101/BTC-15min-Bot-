"""Simple payoff accounting for hypothetical filled YES contracts."""

def summarize(trades: list[dict], price_cents: int = 1, fee_cents: float = 0) -> dict:
    if not 1 <= price_cents <= 99:
        raise ValueError('price_cents must be between 1 and 99')
    count = len(trades)
    wins = sum(int(t['yes_settled']) for t in trades)
    pnl_cents = wins * 100 - count * (price_cents + fee_cents)
    return {'trades_assumed_filled': count, 'wins': wins,
            'win_rate': wins / count if count else 0,
            'pnl_usd': round(pnl_cents / 100, 2)}
