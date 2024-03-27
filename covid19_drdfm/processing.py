"""Processing module for the DFM Synthetic Control Model.

Handles

This model input DataFrame can be generated with a single function:
    - `df = get_df()`
"""

from pathlib import Path

import numpy as np
import pandas as pd
from anndata import AnnData
from sklearn.preprocessing import MinMaxScaler

ROOT_DIR = Path(__file__).parent.absolute()
DATA_DIR = ROOT_DIR / "data/processed"


class Preprocessing:
    """Preprocesses the input data for the DFM Synthetic Control Model."""

    def __init__(self, ad: AnnData):
        """Initializes the Preprocessing object."""
        self.ad = ad
        self.diff_cols = self.get_diff_cols()
        self.log_diff_cols = self.get_logdiff_cols()
        self.df: pd.DataFrame = None

    def process(self) -> pd.DataFrame:
        """Processes the input data for the DFM Synthetic Control Model."""
        self.df = self.ad.to_df()
        if self.diff_cols:
            self.df = self.diff_vars()
        if self.log_diff_cols:
            self.df = self.diff_vars(log=True)
        if self.diff_cols or self.log_diff_cols:
            self.df = self.df.iloc[0]  # Trim first row with NAs
        self.df = normalize(self.df)

        return self.df

    def get_diff_cols(self) -> list[str]:
        """Returns the columns that should be differenced."""
        return self._get_cols("difference")

    def get_logdiff_cols(self) -> list[str]:
        """Returns the columns that should be log-differenced."""
        return self._get_cols("logdiff")

    def _get_cols(self, colname: str) -> list[str]:
        if colname not in self.ad.var.columns:
            return []
        return self.ad.var.query(f"{colname} == True").index.to_list()

    def diff_vars(self, log: bool = False) -> pd.DataFrame:
        """Differences the set of variables within the dataframe
            NOTE: Leaves a row with NAs!

        Args:
            df (pd.DataFrame): Input DataFrame
            cols (List[str]): List of columns to difference
            log bool: Whether to take the log(difference) or not

        Returns:
            pd.DataFrame: DataFrame with given vars differenced
        """
        if log:
            self.df[self.log_diff_cols] = self.df[self.log_diff_cols].apply(lambda x: np.log(x + 1)).diff()
        else:
            self.df[self.diff_cols] = self.df[self.diff_cols].diff()
        return self.df


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize data between 0 and 1

    Args:
        df (pd.DataFrame): State data, pre-normalization

    Returns:
        pd.DataFrame: Normalized and stationary DataFrame
    """
    return pd.DataFrame(MinMaxScaler().fit_transform(df), columns=df.columns)
