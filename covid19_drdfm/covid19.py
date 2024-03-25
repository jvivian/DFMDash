from fractions import Fraction
from functools import reduce
from pathlib import Path
from typing import Optional

import anndata as ann
import fastparquet
import numpy as np
import pandas as pd
import yaml
from anndata import AnnData
from sklearn.preprocessing import MinMaxScaler

from covid19_drdfm.constants import NAME_MAP

ROOT_DIR = Path(__file__).parent.absolute()
DATA_DIR = ROOT_DIR / "data/processed"


def _get_raw_df() -> pd.DataFrame:
    """
    Merges CSV files specified in 'df_paths.txt'. Return a combined DataFrame.

    Returns:
        pd.DataFrame: A pandas DataFrame made from CSV files
    """
    with open(DATA_DIR / "df_paths.txt") as f:
        paths = [ROOT_DIR / x.strip() for x in f.readlines()]
    dfs = [pd.read_csv(x) for x in paths]
    return reduce(lambda x, y: pd.merge(x, y, on=["State", "Year", "Period"], how="left"), dfs)


def get_raw() -> pd.DataFrame:
    """
    Retrieves the raw data as a pandas DataFrame.

    Returns:
        pd.DataFrame: The raw data.
    """
    return (
        _get_raw_df()
        .drop(columns=["Monetary_1_x", "Monetary_11_x"])
        .rename(columns={"Monetary_1_y": "Monetary_1", "Monetary_11_y": "Monetary_11"})
        .drop(columns=["Proportion", "proportion_vax2", "Pandemic_Response_8", "Distributed"])
        .pipe(add_datetime)
        .pipe(fix_names)
    )


def get_df() -> pd.DataFrame:
    """
    Retrieves and processes the raw data to generate a cleaned DataFrame.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    return get_raw().pipe(adjust_inflation).pipe(adjust_pandemic_response)


def get_project_h5ad() -> AnnData:
    """
    Load data.h5ad from the DATA_DIR and return.

    Returns:
        AnnData: The loaded AnnData object.
    """
    return ann.read_h5ad(DATA_DIR / "data.h5ad")


def get_govt_fund_dist() -> list[float]:
    """Reads in govt fund distribution from data/raw/govt_fund_dist.yml

    Returns:
        list[float]: Distribution values. Length equates to num_months
    """
    with open(DATA_DIR / "govt_fund_dist.yml") as f:
        return [float(Fraction(x)) for x in yaml.safe_load(f)]


def adjust_inflation(df: pd.DataFrame) -> pd.DataFrame:
    """Adjust for inflation

    Args:
        df (pd.DataFrame): Input DataFrame (see `get_df`)

    Returns:
        pd.DataFrame: Adjusted DataFrame
    """
    return (
        df.assign(Cons1=lambda x: x.Cons1.div(x.PCE / 100))
        .assign(Cons2=lambda x: x.Cons2.div(x.PCE / 100))
        .assign(Cons3=lambda x: x.Cons3.div(x.PCE / 100))
        .assign(Cons4=lambda x: x.Cons4.div(x.PCE / 100))
        .assign(Cons5=lambda x: x.Cons5.div(x.PCE / 100))
        .assign(GDP=lambda x: x.GDP.div(x.PCE / 100))
        .assign(FixAss=lambda x: x.FixAss.div(x.PCE / 100))
    )


def adjust_pandemic_response(df: pd.DataFrame) -> pd.DataFrame:
    """Adjust pandemic response given fund distribution

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: Adjusted DataFrame
    """
    govt_fund_dist = get_govt_fund_dist()
    responses = ["ARP", "PPP", "CARES"]
    for r in responses:
        df[r] = df[r].astype(float)
        i = df.index[df[r] > 0][0]
        fund = df.loc[i, r]
        for n in range(0, len(govt_fund_dist)):
            df.loc[i + n, r] = fund * govt_fund_dist[n]
    return df


def add_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Set `Time` column to `DateTime` dtype

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: DType adjusted DataFrame
    """
    df = df.assign(Month=pd.to_numeric(df.Period.apply(lambda x: x[1:]))).assign(Day=1)
    df["Time"] = pd.to_datetime({"year": df.Year, "month": df.Month, "day": df.Day})
    return df.drop(columns=["Period", "Month", "Year", "Day"])


def fix_names(df: pd.DataFrame) -> pd.DataFrame:
    """Map sensible names to the merged input dataframe

    Args:
        df (pd.DataFrame): Input DataFrame after merging all input data

    Returns:
        pd.DataFrame: DataFrame with mapped names
    """
    return df.rename(columns=NAME_MAP)
