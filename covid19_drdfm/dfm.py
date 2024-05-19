"""Module for Dynamic Factor `ModelRunner`"""

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
    """
    Represents the result of a dynamic factor model analysis.

    Attributes:
        name (Optional[str]): Name of the batch if batch is specified.
        result (sm.tsa.DynamicFactor): The dynamic factor model result.
        model (sm.tsa.DynamicFactorMQ): The dynamic factor model.
        factors (pd.DataFrame): The factors obtained from the analysis.
    """

    name: Optional[str]
    result: sm.tsa.DynamicFactor
    model: sm.tsa.DynamicFactorMQ
    factors: pd.DataFrame

    def write(self, outdir: Path):
        """
        Writes the model summary, result summary, and factors to CSV files.

        Args:
            outdir (Path): The output directory where the files will be written.
        """
        out = outdir / self.name if self.name else outdir
        with open(out / "model.csv", "w") as f:
            f.write(self.model.summary().as_csv())
        with open(out / "results.csv", "w") as f:
            f.write(self.result.summary().as_csv())
        self.factors.to_csv(out / "factors.csv")


class ModelRunner:
    """
    A class for running dynamic factor models on batches of data.

    Parameters:
    - ad (AnnData): The AnnData object containing the data.
    - outdir (Path, optional): The output directory for saving the results. Defaults to "./output".
    - batch (str, optional): The batch column in the AnnData object. Defaults to None.

    Attributes:
    - ad (AnnData): The AnnData object containing the data.
    - outdir (Path): The output directory for saving the results.
    - batch (str): The batch column in the AnnData object.
    - batches (dict[str, AnnData]): A dictionary of batches extracted from the AnnData object.
    - results (list): A list to store the results of each model run.
    - failures (dict): A dictionary to store any failures that occur during model runs.
    """

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
        """
        Run the dynamic factor models on the batches of data.

        Parameters:
        - maxiter (int, optional): The maximum number of iterations for model fitting. Defaults to 10,000.
        - global_multiplier (int, optional): A global multiplier for the model. Defaults to 1.
        - columns (list[str], optional): The columns to include in the model. Defaults to None.

        Returns:
        - ModelRunner: The ModelRunner object.

        Raises:
        - Exception: If an error occurs during model fitting.
        """
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
            filtered_factors = process_factors(res.factors["filtered"], data.raw, batch.obs)
            result = Result(batch_name, res, model, filtered_factors)
            result.write(self.outdir)
            self.ad.uns["factors"] = result.factors.drop(columns="Time")
            self.ad.write(self.outdir / batch_name / "data.h5ad")
            self.results.append(result)
        # TODO: Concat factors across batch variables
        print("All runs completed!")
        return self

    def write_failures(self):
        """
        Write the failures to a file.

        The failures are written to a file named "failed.txt" in the output directory.
        Each line in the file contains the batch name and the corresponding failure message.
        """
        for name, failure in self.failures.items():
            with open(self.outdir / "failed.txt", "a") as f:
                f.write(f"{name}\t{failure}\n")

    def get_batches(self) -> dict[str, AnnData]:
        """
        Get batches from AnnData object.

        Returns:
        - dict[str, AnnData]: A dictionary of batches extracted from the AnnData object.
        """
        if not self.batch:
            return {None: self.ad}  # Didn't know you could use None as a key, cool
        return {x: self.ad[self.ad.obs[self.batch] == x] for x in self.ad.obs[self.batch].unique()}


def process_factors(factors: pd.DataFrame, raw: pd.DataFrame, obs: pd.DataFrame) -> pd.DataFrame:
    """
    Process factors by merging them with raw and obs dataframes.

    Args:
        factors (pd.DataFrame): The factors dataframe.
        raw (pd.DataFrame): The raw dataframe.
        obs (pd.DataFrame): The obs dataframe.

    Returns:
        pd.DataFrame: The merged factors dataframe.
    """
    factors.index = raw.index
    factors = factors.merge(raw, left_index=True, right_index=True)
    factors.columns = [f"Factor_{x}" for x in factors.columns]
    if not obs.empty:
        factors = factors.merge(obs, left_index=True, right_index=True)
    return factors
