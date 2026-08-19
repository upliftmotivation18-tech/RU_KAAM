# External trace study snapshot

Source: `nvidia/Open-SWE-Traces`, commit `ad4805a5aa7de70d99cab0bb8f99b15304c76de0`.

This study intentionally uses four downloaded public shards: first and last shards for MiniMax-M2.5 under OpenHands and SWE-agent. The snapshot is a reproducible, non-random coverage sample selected by shard position; it is not a claim about the full 207,489-trajectory dataset.

Allowed fields: exact task ID, scaffold, model family, resolved label, structured message turns, explicit tool calls, message character volume, reasoning character volume.

Prohibited claims: token counts, dollar cost, FailureCostRatio, retries, tail-dollar cost, list-price effects.

The analysis requires exact task/model matches between scaffolds and excludes duplicate task/model/scaffold rows.
