from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from anndata import AnnData


@dataclass
class DataLoader:
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
        self.data = ad.X
        self.var = ad.var
        self.obs = ad.obs
        return self

    def dfs_to_ad(self, data: pd.DataFrame, factors: pd.DataFrame, metadata: Optional[pd.DataFrame]) -> AnnData:
        return AnnData(X=data, obs=metadata, var=factors)

    def write_csvs(self, outdir: Path) -> None:
        outdir.mkdir(exist_ok=True)
        self.data.to_csv(outdir / "data.csv")
        self.var.to_csv(outdir / "factors.csv")
        self.obs.to_csv(outdir / "metadata.csv")

    def write_h5ad(self, outdir: Path) -> None:
        outdir.mkdir(exist_ok=True)
        self.ad.write(outdir / "data.h5ad")
