"""Processing module - stores all inputs to run Dynamic Factor Model."""
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml
from anndata import AnnData
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.stattools import adfuller


class DataProcessor:
    def __init__(self, ad: AnnData, global_multiplier: int = 1, maxiter: int = 10_000):
        """Prepares inputs for running model

        Args:
            ad (AnnData): Annotated data object
            global_multiplier (int, optional): Global multiplier. Defaults to 1.
            maxiter (int, optional): Maximum number of iterations. Defaults to 10_000.
        """
        self.ad = ad
        self.global_multiplier = global_multiplier
        self.multiplicities = {"Global": global_multiplier}
        self.maxiter = maxiter
        self.non_stationary_cols = None
        self.raw: pd.DataFrame = None
        self.df: pd.DataFrame = None

    def __repr__(self):
        return f"DataProcessor(ad={self.ad}, global_multiplier={self.global_multiplier}, maxiter={self.maxiter})"

    def process(self, columns: Optional[list[str]] = None) -> "DataProcessor":
        """Processes the data for the Dynamic Factor Model

        Args:
            columns (Optional[list[str]], optional): Subset of columns to use. Defaults to None, which uses all columns.

        Returns:
            DataProcessor: Stores processed data
        """
        filtered_columns = [x for x in columns if x in columns] if columns else None
        if filtered_columns and len(filtered_columns) != len(columns):
            print(f"Invalid columns removed!\nInput: {columns}\nFiltered: {filtered_columns}")
        self.raw = self.ad.to_df()[columns] if columns else self.ad.to_df()
        self.df = self.raw.copy()
        self.process_differences().drop_constant_cols().normalize()
        self.factors = {k: v for k, v in self.get_factors().items() if k in self.df.columns}
        self.stationary_columns = self.get_nonstationary_columns()

        return self

    def write(self, outdir: Path):
        """Writes the processed input data and run info to outdir

        Args:
            outdir (Path): Output directory
        """
        outdir.mkdir(exist_ok=True)
        self.raw.to_csv(outdir / "raw.csv")
        self.df.to_csv(outdir / "df.csv")
        with open(outdir / "run-info.yaml", "w") as f:
            yaml.dump(
                {
                    "factor_map": self.factors,
                    "global_multiplier": self.global_multiplier,
                    "maxiter": self.maxiter,
                    "non_stationary_cols": self.non_stationary_cols,
                    "diff_cols": self.diff_cols,
                    "logdiff_cols": self.logdiff_cols,
                },
                f,
            )

    def get_factors(self) -> dict[str, tuple[str]]:
        """Gets the factor dictionary from the AnnData object for the DFM

        Returns:
            dict[str, tuple[str]]: Dictionary of factors
        """
        if "factor" not in self.ad.var.columns:
            msg = "No `factor` column in AnnData input. Please add to `.var`"
            raise RuntimeError(msg)
        factors = self.ad.var.factor.to_dict()
        if self.global_multiplier == 0:
            return {k: (v,) for k, v in factors.items()}
        return {k: ("Global", v) for k, v in factors.items()}

    def process_differences(self) -> "DataProcessor":
        """Processes the differences in the data

        Returns:
            DataProcessor: Processed data
        """
        self.diff_cols = self.get_diff_cols()
        self.logdiff_cols = self.get_logdiff_cols()
        if self.diff_cols:
            self.diff_vars()
        if self.logdiff_cols:
            self.logdiff_vars()
        if self.diff_cols or self.logdiff_cols:
            self.df = self.df.iloc[1:]
            self.raw = self.raw.iloc[1:]  # Trim raw dataframe for parity
        self.df = self.df.fillna(0)
        return self

    def drop_constant_cols(self) -> "DataProcessor":
        """Drops constant columns from the DataFrame.

        Returns:
            DataProcessor: Processed data
        """
        self.df = self.df.loc[:, self.df.columns[~self.df.apply(is_constant)]]
        return self

    def get_diff_cols(self) -> list[str]:
        """Returns the columns that should be differenced.

        Returns:
            list[str]: List of columns to be differenced
        """
        return self._get_cols("difference")

    def get_logdiff_cols(self) -> list[str]:
        """Returns the columns that should be log-differenced.

        Returns:
            list[str]: List of columns to be log-differenced
        """
        return self._get_cols("logdiff")

    def _get_cols(self, colname: str) -> list[str]:
        """Helper function to get columns based on a specific condition

        Args:
            colname (str): Name of the condition

        Returns:
            list[str]: List of columns that satisfy the condition
        """
        if colname not in self.ad.var.columns:
            return []
        columns = self.ad.var.query(f"{colname} == True").index.to_list()
        return [x for x in columns if x in self.df.columns]

    def diff_vars(self) -> "DataProcessor":
        """Performs differencing on the specified columns

        Returns:
            DataProcessor: Processed data
        """
        self.df[self.diff_cols] = self.df[self.diff_cols].diff()
        return self

    def logdiff_vars(self) -> "DataProcessor":
        """Performs log-differencing on the specified columns

        Returns:
            DataProcessor: Processed data
        """
        self.df[self.logdiff_cols] = self.df[self.logdiff_cols].apply(lambda x: np.log(x + 1)).diff()
        return self

    def get_nonstationary_columns(self) -> list[str]:
        """Runs AD-Fuller test on columns and returns non-stationary columns

        Returns:
            list[str]: List of non-stationary columns
        """
        cols = []
        for col in self.df.columns:
            result = adfuller(self.df[col])
            p_value = result[1]
            if p_value > 0.25:  # TODO: Ask Aaron/Josh - p-value 0.25 is pretty weird
                cols.append(col)
        print(f"Columns that fail the ADF test (non-stationary)\n{cols}")
        return cols

    def normalize(self) -> "DataProcessor":
        """Normalizes the data between 0 and 1

        Returns:
            DataProcessor: Processed data
        """
        self.df = pd.DataFrame(MinMaxScaler().fit_transform(self.df), columns=self.df.columns)
        self.df.index = self.raw.index
        return self


def is_constant(column) -> bool:
    """Returns True if a DataFrame column is constant"""
    return all(column == column.iloc[0])
