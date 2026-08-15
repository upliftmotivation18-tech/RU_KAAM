import hashlib
import json
import warnings
from pathlib import Path

import pandas as pd
import pytest

from scripts.run_analysis import (
    FROZEN_INPUT_SHA256,
    add_frontiers,
    file_sha256,
    fixed_scaffold_pairwise_analysis,
    load_data,
    verify_frozen_input,
)


def test_loaded_source_has_expected_number_of_rows_and_no_duplicate_displayed_runs():
    data = load_data(Path("data/all_leaderboards_costs_HAL.csv"))

    assert len(data) == 242
    assert not data.duplicated(["benchmark", "scaffold", "model_configuration"]).any()


def test_default_frozen_source_hash_matches_manifest_and_verifier():
    source = Path("data/all_leaderboards_costs_HAL.csv")

    assert file_sha256(source) == FROZEN_INPUT_SHA256
    assert verify_frozen_input(source) == FROZEN_INPUT_SHA256


def test_primary_generalist_pairwise_analysis_has_fifteen_pairs_with_minimum_overlap():
    data = add_frontiers(load_data(Path("data/all_leaderboards_costs_HAL.csv")))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pairwise, rates = fixed_scaffold_pairwise_analysis(data, n_bootstrap=100, seed=11)

    assert len(pairwise) == 15
    assert pairwise["n_shared"].min() >= 5
    assert (pairwise["n_configuration_resamples"] == 100).all()
    assert (pairwise["accuracy_spearman_n_valid_resamples"] > 0).all()
    assert len(rates) >= 20


def test_scicode_swe_pair_is_the_expected_low_transfer_sanity_check():
    data = add_frontiers(load_data(Path("data/all_leaderboards_costs_HAL.csv")))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pairwise, _ = fixed_scaffold_pairwise_analysis(data, n_bootstrap=100, seed=11)

    row = pairwise.loc[
        (pairwise["benchmark_a"] == "scicode")
        & (pairwise["benchmark_b"] == "swebench_verified_mini")
    ].iloc[0]

    assert row["n_shared"] == 9
    assert row["accuracy_spearman"] == pytest.approx(0.150466, abs=1e-5)
    assert row["cost_spearman"] == pytest.approx(0.016667, abs=1e-5)


def test_output_metadata_records_actual_cli_bootstrap_setting():
    metadata_path = Path("outputs/analysis_metadata.json")
    if not metadata_path.exists():
        pytest.skip("Run the pipeline before checking generated metadata")
    metadata = json.loads(metadata_path.read_text())

    assert metadata["source_csv_sha256"] == FROZEN_INPUT_SHA256
    assert metadata["configuration_resamples"] == 5_000
    assert metadata["matching_unit"].startswith("Exact public HAL Models display label")
