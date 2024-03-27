"""Processing module - stores all inputs to run Dynamic Factor Model."""
import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from anndata import AnnData
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.stattools import adfuller


class DataProcessor:
    def __init__(self, ad: AnnData, global_multiplier: int = 1, maxiter: int = 10_000):
        """Prepares inputs for running model"""
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
        outdir.mkdir(exist_ok=True)
        self.raw.to_csv(outdir / "raw.csv")
        self.df.to_csv(outdir / "df.csv")
        with open(outdir / "run-info.json", "w") as f:
            json.dump(
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
        if "factor" not in self.ad.var.columns:
            msg = "No `factor` column in AnnData input. Please add to `.var`"
            raise RuntimeError(msg)
        factors = self.ad.var.factor.to_dict()
        if self.global_multiplier == 0:
            return {k: (v,) for k, v in factors.items()}
        return {k: ("Global", v) for k, v in factors.items()}

    def process_differences(self) -> "DataProcessor":
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
        """Drops constant columns from the DataFrame."""
        self.df = self.df.loc[:, self.df.columns[~self.df.apply(is_constant)]]
        return self

    def get_diff_cols(self) -> list[str]:
        """Returns the columns that should be differenced."""
        return self._get_cols("difference")

    def get_logdiff_cols(self) -> list[str]:
        """Returns the columns that should be log-differenced."""
        return self._get_cols("logdiff")

    def _get_cols(self, colname: str) -> list[str]:
        if colname not in self.df.columns:
            return []
        return self.ad.var.query(f"{colname} == True").index.to_list()

    def diff_vars(self) -> "DataProcessor":
        self.df[self.diff_cols] = self.df[self.diff_cols].diff()
        return self

    def logdiff_vars(self) -> "DataProcessor":
        self.df[self.logdiff_cols] = self.df[self.logdiff_cols].apply(lambda x: np.log(x + 1)).diff()
        return self

    def get_nonstationary_columns(self) -> list[str]:
        """Run AD-Fuller on tests and report failures

        Returns:
            Model: Model with non-stationary columns
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
        """Normalize data between 0 and 1

        Args:
            df (pd.DataFrame): State data, pre-normalization

        Returns:
            pd.DataFrame: Normalized and stationary DataFrame
        """
        self.df = pd.DataFrame(MinMaxScaler().fit_transform(self.df), columns=self.df.columns)
        self.df.index = self.raw.index
        return self


def is_constant(column) -> bool:
    """Returns True if a DataFrame column is constant"""
    return all(column == column.iloc[0])
