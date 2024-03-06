import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

from covid19_drdfm.dfm import run_parameterized_model
from covid19_drdfm.processing import get_df

COLUMNS = ["PCE", "CPIU", "Hosp1", "Deaths1"]


def test_run_model():
    """
    Test the run_parameterized_model function.

    This function tests the run_parameterized_model function by running it with a sample dataframe,
    a state code, and a test directory path. It then asserts that the model.csv and results.csv files
    are created in the test directory, and finally removes the test directory.

    Returns:
        None
    """
    df = get_df()
    state = "SD"
    run_parameterized_model(df, state, Path("./testdir"), columns=COLUMNS, global_multiplier=1)
    assert Path("./testdir/SD/model.csv").exists()
    assert Path("./testdir/SD/results.csv").exists()
    shutil.rmtree("./testdir")


def test_run_model_global_0():
    """
    Test the run_parameterized_model function with a global multipler of 0.

    This function tests the run_parameterized_model function by running it with a sample dataframe,
    a state code, and a test directory path. It then asserts that the model.csv and results.csv files
    are created in the test directory, and finally removes the test directory.

    Returns:
        None
    """
    df = get_df()
    state = "SD"
    run_parameterized_model(df, state, Path("./testdir"), columns=COLUMNS, global_multiplier=0)
    assert Path("./testdir/SD/model.csv").exists()
    assert Path("./testdir/SD/results.csv").exists()
    shutil.rmtree("./testdir")


def test_run_failure():
    """
    Test the run_parameterized_model function for a state with known failure conditions

    This function tests the run_parameterized_model function by running it with a sample dataframe,
    a state code, and a test directory path. It then asserts that the model.csv and results.csv files
    are created in the test directory, and finally removes the test directory.

    Returns:
        None
    """
    df = get_df()
    date_object = datetime.strptime("2019-01-01", "%Y-%m-%d")
    df = df[df.Time > date_object]
    state = "WY"
    run_parameterized_model(df, state, Path("./testdir"), global_multiplier=2)
    assert Path("./testdir/failed.txt").exists()
    shutil.rmtree("./testdir")


def test_modified_start_date():
    """
    Test the run_parameterized_model function with a modified start date

    This function tests the run_parameterized_model function by running it with a sample dataframe,
    a state code, and a test directory path. It then asserts that the model.csv and results.csv files
    are the same length (due to subsetting on time)

    Returns:
        None
    """
    df = get_df()
    date_string = "2020-01-01"
    columns = ["PCE", "CPIU", "Hosp1", "Deaths1"]
    date_object = datetime.strptime(date_string, "%Y-%m-%d")
    df = df[df.Time > date_object]
    state = "CA"
    test_dir = Path("./testdir")
    run_parameterized_model(df, state, test_dir, columns=columns, global_multiplier=2)
    assert pd.read_csv(test_dir / state / "raw.csv").shape == pd.read_csv(test_dir / state / "df.csv").shape
    shutil.rmtree("./testdir")
