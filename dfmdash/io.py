"""IO module containing `DataLoader` for interop between DataFrames/CSVs and AnnData H5AD"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from anndata import AnnData


@dataclass
class DataLoader:
    """
    A class for loading and manipulating data for the DFMDash project.

    Attributes:
        ad (Optional[AnnData]): An optional AnnData object representing the loaded data.
        data (Optional[pd.DataFrame]): An optional pandas DataFrame representing the data.
        var (Optional[pd.DataFrame]): An optional pandas DataFrame representing the factors.
        obs (Optional[pd.DataFrame]): An optional pandas DataFrame representing the metadata.

    Methods:
        load(data: Path, factors: Path, metadata: Optional[Path] = None) -> DataLoader:
            Loads the data, factors, and metadata from the specified paths and returns the DataLoader object.
        convert(ad: AnnData) -> DataLoader:
            Converts the provided AnnData object to DataLoader format and returns the DataLoader object.
        dfs_to_ad(data: pd.DataFrame, factors: pd.DataFrame, metadata: Optional[pd.DataFrame]) -> AnnData:
            Converts the provided pandas DataFrames to an AnnData object and returns it.
        write_csvs(outdir: Path) -> DataLoader:
            Writes the data, factors, and metadata to CSV files in the specified output directory and returns the DataLoader object.
        write_h5ad(outdir: Path) -> DataLoader:
            Writes the AnnData object to an H5AD file in the specified output directory and returns the DataLoader object.
    """

    ad: Optional[AnnData] = None
    data: Optional[pd.DataFrame] = None
    var: Optional[pd.DataFrame] = None
    obs: Optional[pd.DataFrame] = None

    def load(self, data: Path, factors: Path, metadata: Optional[Path] = None) -> "DataLoader":
        self.data = pd.read_csv(data)
        self.var = pd.read_csv(factors, index_col=0)
        self.obs = pd.read_csv(metadata, index_col=0) if metadata else None
        self.ad = self.dfs_to_ad(self.data, self.var, self.obs)
        return self

    def convert(self, ad: AnnData) -> "DataLoader":
        self.ad = ad
        self.data = ad.to_df()
        self.var = ad.var
        self.obs = ad.obs
        return self

    def dfs_to_ad(self, data: pd.DataFrame, factors: pd.DataFrame, metadata: Optional[pd.DataFrame]) -> AnnData:
        data = data[factors.index]  # Force dataframe to be in same order as factor input
        return AnnData(X=data, obs=metadata, var=factors)

    def write_csvs(self, outdir: Path) -> "DataLoader":
        outdir.mkdir(exist_ok=True)
        self.data.to_csv(outdir / "data.csv")
        self.var.to_csv(outdir / "factors.csv")
        self.obs.to_csv(outdir / "metadata.csv")
        return self

    def write_h5ad(self, outdir: Path) -> "DataLoader":
        outdir.mkdir(exist_ok=True)
        self.ad.write(outdir / "data.h5ad")
        return self
