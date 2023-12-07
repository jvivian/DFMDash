"""I/O and processing module

Converts all input files into single consolidated dataframe that can be used
downstream as model input

This model input DataFrame can be generated with a single function:
    - `df = run()`
"""

from fractions import Fraction
from functools import reduce
from pathlib import Path

import fastparquet
import numpy as np
import pandas as pd
import yaml
from sklearn.preprocessing import MinMaxScaler

from covid19_drdfm.constants import DIFF_COLS, LOG_DIFF_COLS, NAME_MAP

ROOT_DIR = Path(__file__).parent.absolute()
DATA_DIR = ROOT_DIR / "data/processed"


def get_df() -> pd.DataFrame:
    """Read input DataFrames and merge

    Returns:
        pd.DataFrame: Merged DataFrame
    """
    with open(DATA_DIR / "df_paths.txt") as f:
        paths = [ROOT_DIR / x.strip() for x in f.readlines()]
    dfs = [pd.read_csv(x) for x in paths]
    return (
        reduce(lambda x, y: pd.merge(x, y, on=["State", "Year", "Period"], how="left"), dfs)
        .fillna(0)
        .drop(columns=["Monetary_1_x", "Monetary_11_x"])
        .rename(columns={"Monetary_1_y": "Monetary_1", "Monetary_11_y": "Monetary_11"})
        .drop(
            columns=["Proportion", "proportion_vax2", "Pandemic_Response_8"]
        )  #! Columns removed per discussion with AC
        .pipe(adjust_inflation)
        .pipe(add_datetime)
        .pipe(fix_names)
        .pipe(adjust_pandemic_response)
        .pipe(diff_vars, cols=DIFF_COLS)
        .pipe(diff_vars, cols=LOG_DIFF_COLS, log=True)
        .fillna(0)
        .pipe(normalize)
        .drop(index=0)  # Drop first row with NaNs from diff
    )


def write(df: pd.DataFrame, outpath: Path):
    """Write dataframe given the extension"""
    ext = outpath.suffix
    if ext == ".xlsx":
        df.to_excel(outpath)
    elif ext == ".csv":
        df.to_csv(outpath)
    elif ext == ".parq" or ext == ".parquet":
        fastparquet.write(df, outpath)
    else:
        raise OSError


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
        df.assign(Demand_1=lambda x: x.Demand_1.div(x.Monetary_3 / 100))
        .assign(Demand_2=lambda x: x.Demand_2.div(x.Monetary_3 / 100))
        .assign(Demand_3=lambda x: x.Demand_3.div(x.Monetary_3 / 100))
        .assign(Demand_4=lambda x: x.Demand_4.div(x.Monetary_3 / 100))
        .assign(Demand_5=lambda x: x.Demand_5.div(x.Monetary_3 / 100))
        .assign(Supply_1=lambda x: x.Supply_1.div(x.Monetary_3 / 100))
        .assign(Supply_6=lambda x: x.Supply_6.div(x.Monetary_3 / 100))
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


def diff_vars(df: pd.DataFrame, cols: list[str], log: bool = False) -> pd.DataFrame:
    """Differences the set of variables within the dataframe
        NOTE: Leaves a row with Nas


    Args:
        df (pd.DataFrame): Input DataFrame
        cols (List[str]): List of columns to difference
        log bool: Whether to take the log(difference) or not

    Returns:
        pd.DataFrame: DataFrame with given vars differenced
    """
    if log:
        # df[cols] = np.log(df[cols]).diff().fillna(0).apply(lambda x: np.log(x + 0))
        df[cols] = df[cols].apply(lambda x: np.log(x + 1)).diff()
    else:
        df[cols] = df[cols].diff()
    return df


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize data and make stationary - scaling for post-DFM Synthetic Control Model

    Args:
        df (pd.DataFrame): State data, pre-normalization

    Returns:
        pd.DataFrame: Normalized and stationary DataFrame
    """
    meta_cols = df[["State", "Time"]]
    # df = df.drop(columns=["Time"]) if "Time" in df.columns else df
    df = df.drop(columns=["State", "Time"])
    # Normalize data
    scaler = MinMaxScaler()
    new = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
    new["State"] = meta_cols["State"]
    return new
