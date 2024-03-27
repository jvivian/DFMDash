import shutil
import pandas as pd
import numpy as np
from pathlib import Path
from anndata import AnnData
from covid19_drdfm.io import DataLoader
from covid19_drdfm.covid19 import DATA_DIR
import pytest

@pytest.fixture()
def dfs():
    data = pd.read_csv(DATA_DIR / 'data.csv')
    factors = pd.read_csv(DATA_DIR / 'factors.csv', index_col=0)
    metadata = pd.read_csv(DATA_DIR / 'metadata.csv', index_col=0)
    return data, factors, metadata
    

def test_load(tmpdir):
    outdir = Path(tmpdir / 'test_load')
    outdir.mkdir(exist_ok=True)
    loader = DataLoader()
    data_path = outdir / "./test_data.csv"
    factors_path = outdir / "./test_factors.csv"
    metadata_path = outdir / "./test_metadata.csv"

    test_data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    test_factors = pd.DataFrame({"factor": ["Zoo", 'Zoo']}, index=['A', 'B'])
    test_metadata = pd.DataFrame({"State": ["S1", "S2", "S3"]})

    test_data.to_csv(data_path, index=False)
    test_factors.to_csv(factors_path, index=True)
    test_metadata.to_csv(metadata_path, index=True)

    loader.load(data_path, factors_path, metadata_path)

    assert isinstance(loader.ad, AnnData)
    assert isinstance(loader.data, pd.DataFrame)
    assert isinstance(loader.var, pd.DataFrame)
    assert isinstance(loader.obs, pd.DataFrame)

    assert loader.data.equals(test_data)
    assert loader.var.equals(test_factors)
    assert loader.obs.equals(test_metadata)

    shutil.rmtree(outdir)

def test_convert():
    loader = DataLoader()

    ad = AnnData(X=np.array([[1, 2], [3, 4]]), obs=pd.DataFrame({"Sample": ["S1", "S2"]}), var=pd.DataFrame({"Factor": ["X", "Y"]}))
    loader.convert(ad)

    assert loader.ad is ad
    assert loader.data.equals(ad.to_df())
    assert loader.var.equals(ad.var)
    assert loader.obs.equals(ad.obs)

def test_write_csvs(tmpdir):
    loader = DataLoader()
    outdir = Path(tmpdir / 'test_csvs')

    loader.data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    loader.var = pd.DataFrame({"Factor": ["X", "Y", "Z"]})
    loader.obs = pd.DataFrame({"Sample": ["S1", "S2", "S3"]})
    loader.write_csvs(outdir)

    assert (outdir / "data.csv").exists()
    assert (outdir / "factors.csv").exists()
    assert (outdir / "metadata.csv").exists()

    shutil.rmtree(outdir)

def test_write_h5ad(tmpdir):
    loader = DataLoader()
    outdir = Path(tmpdir / 'test_h5ad')

    loader.ad = AnnData(X=np.array([[1, 2], [3, 4]]), obs=pd.DataFrame({"Sample": ["S1", "S2"]}), var=pd.DataFrame({"Factor": ["X", "Y"]}))
    loader.write_h5ad(outdir)
    assert (outdir / "data.h5ad").exists()

    shutil.rmtree(outdir)
