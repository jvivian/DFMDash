from pathlib import Path
import os

from covid19_drdfm.dfm import run_model
from covid19_drdfm.processing import run


def test_run_model():
    raw = run()
    run_model(raw, "NY", "./")
    assert Path("./model.csv").exists()
    assert Path("./results.csv").exists()
    os.remove("./model.csv")
    os.remove("./results.csv")
