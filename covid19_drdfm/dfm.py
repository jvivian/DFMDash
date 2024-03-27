"""Module for Dynamic Factor ModelRunner"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
import statsmodels.api as sm
from anndata import AnnData
from rich import print
from rich.progress import track

from covid19_drdfm.processing import DataProcessor


@dataclass
class Result:
    name: Optional[str]  # Name of batch if batch is specified
    result: sm.tsa.DynamicFactor
    model: sm.tsa.DynamicFactorMQ
    factors: pd.DataFrame

    def write(self, outdir: Path):
        out = outdir / self.name if self.name else outdir
        with open(out / "model.csv", "w") as f:
            f.write(self.model.summary().as_csv())
        with open(out / "results.csv", "w") as f:
            f.write(self.result.summary().as_csv())
        self.factors.to_csv(out / "factors.csv")


class ModelRunner:
    def __init__(self, ad: AnnData, outdir: Path = Path("./output"), batch: Optional[str] = None):
        self.ad = ad
        self.outdir = outdir
        self.batch = batch
        self.batches: dict[str, AnnData] = self.get_batches()
        self.results = []
        self.failures = {}

    def __repr__(self):
        return f"ModelRunner(ad={self.ad}, outdir={self.outdir}, batch={self.batch})"

    def run(self, maxiter=10_000, global_multiplier=1, columns: Optional[list[str]] = None) -> "ModelRunner":
        self.outdir.mkdir(exist_ok=True)
        print(f"{len(self.batches)} batches to run")
        for batch_name, batch in track(list(self.batches.items())):
            data = DataProcessor(batch, global_multiplier, maxiter).process(columns)
            data.write(self.outdir / batch_name) if batch_name else data.write(self.outdir)
            model = sm.tsa.DynamicFactorMQ(data.df, factors=data.factors, factor_multiplicities=data.multiplicities)
            try:
                res = model.fit(disp=10, maxiter=data.maxiter)
            except Exception as e:
                self.failures[batch_name] = e
                continue
            filtered_factors = self.process_factors(res.factors["filtered"], data.raw, batch.obs)
            result = Result(batch_name, res, model, filtered_factors)
            result.write(self.outdir)
            self.results.append(result)
        return self

    def write_failures(self, outdir: str):
        for name, failure in self.failures.items():
            with open(outdir / "failed.txt", "a") as f:
                f.write(f"{name}\t{failure}\n")

    def process_factors(self, factors: pd.DataFrame, raw: pd.DataFrame, obs: pd.DataFrame) -> pd.DataFrame:
        factors.index = raw.index
        factors = factors.merge(raw, left_index=True, right_index=True)
        factors.columns = [f"Factor_{x}" for x in factors.columns]
        if not obs.empty:
            factors = factors.merge(obs, left_index=True, right_index=True)
        return factors

    def get_batches(self) -> dict[str, AnnData]:
        """Get batches from AnnData object"""
        if not self.batch:
            return {None: self.ad}  # Didn't know you could use None as a key, cool
        return {x: self.ad[self.ad.obs[self.batch] == x] for x in self.ad.obs[self.batch].unique()}
