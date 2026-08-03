# The orders pipeline

`orders_daily` is rebuilt every morning at 06:00 UTC from the `orders_raw` capture and the
`customers` dimension. The job is idempotent: rerunning it for a date replaces that date's
partition rather than appending to it.

The 06:00 slot was chosen because the upstream capture closes at 05:30 and the downstream
finance extract starts at 07:00. That leaves thirty minutes of slack in front and an hour
behind, which has absorbed every late capture seen so far except the quarter-end batches.

## Reruns

Reruns are safe and are the normal repair. There is no separate backfill job — a backfill
is a rerun over a date range.
