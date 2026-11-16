"""Minimal labeled reversal interface; labels must be validated on real data."""

def is_reversal(row: dict) -> bool:
    """Return a precomputed major-reversal label, without look-ahead."""
    return str(row['reversal']).strip() == '1'
