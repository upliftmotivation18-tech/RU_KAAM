import json
import subprocess
import sys
from pathlib import Path


def test_cli_metadata_reflects_requested_bootstrap_count(tmp_path: Path):
    output = tmp_path / "analysis"
    command = [
        sys.executable,
        "scripts/run_analysis.py",
        "--output",
        str(output),
        "--bootstrap",
        "25",
    ]

    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    assert completed.returncode == 0

    metadata = json.loads((output / "analysis_metadata.json").read_text())
    pairwise = output / "tables" / "generalist_pairwise_transfer.csv"
    assert metadata["configuration_resamples"] == 25
    assert metadata["source_csv_sha256"] == "f8a07cbe6aae2801f592df3db7432a91c32a3de63dcf3ac4e0b5896bd34731f0"
    assert pairwise.exists()
    assert (output / "figures" / "rank_transfer_similarity.png").exists()
