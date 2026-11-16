# Strategy specification (prototype)

- Market: Kalshi 15-minute Bitcoin event contracts.
- Candidate bid: 1 cent per YES contract in the demonstration only.
- Signal: externally labeled reversal (`reversal=1`).
- Cooldown: skip the reversal market and the next N completed markets; default N=50.
- Entry: on later eligible markets, assume a 1-cent bid fills for *toy simulation only*.
- Outcome: contract pays $1 if YES settles, otherwise $0.

## Not implemented

Live API, authenticated order entry, cancellation, realistic fills, position sizing, contract-side selection, fee schedule, and risk limits. Historical outcome labels cannot be used to make same-interval decisions.
