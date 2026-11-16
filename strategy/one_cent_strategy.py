"""Generate illustrative entry signals from pre-labeled market rows."""
from strategy.cooldown import eligible
from strategy.reversal_detector import is_reversal


def signals(rows: list[dict], cooldown: int = 50) -> list[dict]:
    """Return eligible rows; do not enter on a reversal-labeled market."""
    last_reversal = None
    output = []
    for row in sorted(rows, key=lambda r: int(r['interval_index'])):
        index = int(row['interval_index'])
        if is_reversal(row):
            last_reversal = index
            continue
        if eligible(index, last_reversal, cooldown):
            output.append(row)
    return output
