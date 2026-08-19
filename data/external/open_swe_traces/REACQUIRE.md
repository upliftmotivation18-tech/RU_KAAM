# Reacquiring the external Open-SWE trace sample

The external matched trajectory-burden extension uses four public Parquet shards from the Hugging Face dataset [`nvidia/Open-SWE-Traces`](https://huggingface.co/datasets/nvidia/Open-SWE-Traces), source commit:

```text
ad4805a5aa7de70d99cab0bb8f99b15304c76de0
```

The Parquet files are intentionally excluded from Git because they total roughly 852 MB. They are included in the locally generated anonymous supplement archive but can also be re-acquired exactly with `huggingface_hub`:

```python
from huggingface_hub import hf_hub_download
from pathlib import Path

files = [
    "data/minimax_m25_openhands_trajectories/train-00000-of-00020.parquet",
    "data/minimax_m25_openhands_trajectories/train-00019-of-00020.parquet",
    "data/minimax_m25_sweagent_trajectories/train-00000-of-00023.parquet",
    "data/minimax_m25_sweagent_trajectories/train-00022-of-00023.parquet",
]
outputs = [
    "minimax_openhands_shard00.parquet",
    "minimax_openhands_shard19.parquet",
    "minimax_sweagent_shard00.parquet",
    "minimax_sweagent_shard22.parquet",
]
root = Path("data/external/open_swe_traces")
root.mkdir(parents=True, exist_ok=True)
for source, output in zip(files, outputs, strict=True):
    cached = hf_hub_download(
        repo_id="nvidia/Open-SWE-Traces",
        repo_type="dataset",
        revision="ad4805a5aa7de70d99cab0bb8f99b15304c76de0",
        filename=source,
    )
    (root / output).write_bytes(Path(cached).read_bytes())
```

Expected SHA-256 checksums:

| File | SHA-256 |
|---|---|
| `minimax_openhands_shard00.parquet` | `a3b289c8d93aa9327782088cf389782d9b088f2c0c69c7417f2f17ff49d3369f` |
| `minimax_openhands_shard19.parquet` | `d1d2ebc39fb8c70e4ff5b79790d64c1e742b477ff97935bb4f8614573e137fba` |
| `minimax_sweagent_shard00.parquet` | `fa43c50eaacf26d75e2e68bbd81f7dc60c10ade071b4bd6d33bfc4ee2cbf9d0f` |
| `minimax_sweagent_shard22.parquet` | `3a448b25720dbb712ac41348f5da51fd3baf4c82da2dfe4e54460e215429f621` |

The analysis script `scripts/run_external_trace_study.py` expects these files under this directory. Do not replace the documented boundary sample with a different shard selection without changing the study description.
