import pandas as pd
import pytest

from dfmdash.covid19 import ROOT_DIR
from dfmdash.results import parse_multiple_runs, parse_results, parse_run_results


@pytest.fixture
def runs_dir() -> pd.DataFrame:
    return ROOT_DIR / "../data" / "example-data"


@pytest.fixture
def run_path(runs_dir) -> pd.DataFrame:
    return runs_dir / "pandemic-only"


@pytest.fixture
def result_path(run_path) -> pd.DataFrame:
    return run_path / "AK" / "results.csv"


def test_parse_results(result_path):
    # Call the function
    df = parse_results(result_path)

    # Check the extracted values
    assert df["Log Likelihood"][0] < -1000
    assert df["AIC"][0] > 0
    assert df["EM Iterations"][0] > 30


def test_parse_run_results(run_path):
    df = parse_run_results(run_path)
    assert df.shape == (50, 4)


def test_parse_multiple_runs(runs_dir):
    df = parse_multiple_runs(runs_dir)
    assert df.shape == (196, 5)
