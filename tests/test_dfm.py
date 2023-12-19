import os
import shutil
from pathlib import Path

from covid19_drdfm.dfm import run_model
from covid19_drdfm.processing import get_df


# TODO: output should go in a directory instead of dumping shit everywhere
def test_run_model():
    df = get_df()
    state = "SD"
    run_model(df, state, Path("./testdir"))
    assert Path("./testdir/SD/model.csv").exists()
    assert Path("./testdir/SD/results.csv").exists()
    shutil.rmtree("./testdir")
