"""Completed-market cooldown logic."""

def eligible(interval_index: int, last_reversal: int | None, cooldown: int) -> bool:
    """Permit an entry only after the full cooldown has elapsed."""
    if cooldown < 0:
        raise ValueError('cooldown must be nonnegative')
    return last_reversal is None or interval_index > last_reversal + cooldown
