import shutil
from pathlib import Path

from covid19_drdfm.dfm import run_parameterized_model
from covid19_drdfm.processing import get_df


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
    run_parameterized_model(df, state, Path("./testdir"), global_multiplier=1)
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
    run_parameterized_model(df, state, Path("./testdir"), global_multiplier=0)
    assert Path("./testdir/SD/model.csv").exists()
    assert Path("./testdir/SD/results.csv").exists()
    shutil.rmtree("./testdir")
