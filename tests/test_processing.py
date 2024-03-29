from functools import reduce

import pandas as pd
import pytest
from pathlib import Path

from covid19_drdfm.covid19 import get_project_h5ad
from covid19_drdfm.processing import DataProcessor, is_constant


@pytest.fixture()
def data():
    ad = get_project_h5ad()
    ad = ad[ad.obs.State == "AK", :]
    return DataProcessor(ad)


def test_process(data):
    data = data.process()
    assert isinstance(data.df, pd.DataFrame)
    assert isinstance(data.raw, pd.DataFrame)
    assert isinstance(data, DataProcessor)


def test_write(data, tmpdir):
    data = data.process()
    outdir = Path(tmpdir) / "output"
    data.write(outdir)
    assert (outdir / "df.csv").exists()
    assert (outdir / "raw.csv").exists()
    assert (outdir / "run-info.json").exists()


def test_get_factors(data):
    factors = data.get_factors()
    assert isinstance(factors, dict)


def test_is_constant():
    column = pd.Series([1, 1, 1, 1])
    result = is_constant(column)
    assert result is True
