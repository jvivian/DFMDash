import pandas as pd
import pytest

from covid19_drdfm.processing import ROOT_DIR
from covid19_drdfm.results import parse_multiple_runs, parse_results, parse_run_results


@pytest.fixture
def runs_dir() -> pd.DataFrame:
    return ROOT_DIR / "data" / "example-data"


@pytest.fixture
def run_path(runs_dir) -> pd.DataFrame:
    return runs_dir / "run1"


@pytest.fixture
def result_path(run_path) -> pd.DataFrame:
    return run_path / "AK" / "results.csv"


def test_parse_results(result_path):
    # Call the function
    df = parse_results(result_path)

    # Check the extracted values
    assert df["Log Likelihood"][0] == 1263.116
    assert df["AIC"][0] == -2342.233
    assert df["EM Iterations"][0] == 49


def test_parse_run_results(run_path):
    # Call the function
    df = parse_run_results(run_path)

    # Check the extracted values
    assert df.shape == (50, 4)


def test_parse_multiple_runs(runs_dir):
    # Create a temporary directory with multiple run directories
    df = parse_multiple_runs(runs_dir)

    # Check the extracted values
    assert df.shape == (97, 5)
