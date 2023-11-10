import os
import shutil
from pathlib import Path

from covid19_drdfm.dfm import run_model
from covid19_drdfm.processing import get_df


# TODO: output should go in a directory instead of dumping shit everywhere
def test_run_model():
    df = get_df()
    run_model(df, "NY", Path("./testdir"))
    assert Path("./testdir/NY/model.csv").exists()
    assert Path("./testdir/NY/results.csv").exists()
    shutil.rmtree("./testdir")
