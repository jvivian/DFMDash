"""I/O and processing module

Converts all input files into single consolidated dataframe that can be used
downstream as model input

This model input DataFrame can be generated with a single function:
    - `df = get_df()`
"""

from fractions import Fraction
from functools import reduce
from pathlib import Path

import fastparquet
import numpy as np
import pandas as pd
import yaml
from sklearn.preprocessing import MinMaxScaler

from covid19_drdfm.constants import NAME_MAP

ROOT_DIR = Path(__file__).parent.absolute()
DATA_DIR = ROOT_DIR / "data/processed"


def _get_raw_df() -> pd.DataFrame:
    """
    Reads multiple CSV files specified in 'df_paths.txt' and return a combined pandas DataFrames.

    Returns:
        pd.DataFrame: A pandas DataFrames containing the data from the CSV files.
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
        .pipe(fix_names)
    )


def get_df() -> pd.DataFrame:
    """
    Retrieves and processes the raw data to generate a cleaned DataFrame.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    return get_raw().pipe(adjust_inflation).pipe(add_datetime).pipe(adjust_pandemic_response)


def write(df: pd.DataFrame, outpath: Path) -> None:
    """
    Write a pandas DataFrame to a file.

    Parameters:
        df (pd.DataFrame): The DataFrame to be written.
        outpath (Path): The path to the output file.

    Raises:
        OSError: If the file extension is not supported.

    Returns:
        None
    """
    ext = outpath.suffix
    if ext == ".xlsx":
        df.to_excel(outpath)
    elif ext == ".csv":
        df.to_csv(outpath)
    elif ext == ".parq" or ext == ".parquet":
        fastparquet.write(df, outpath)
    elif ext == ".tsv":
        df.to_csv(df, outpath, sep="\t")
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
    meta_cols = df[["State", "Time"]].copy().reset_index(drop=True)
    df = df.drop(columns=["State", "Time"])
    # Normalize data
    scaler = MinMaxScaler()
    new = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
    new["State"] = meta_cols["State"]
    new["Time"] = meta_cols["Time"]
    return new
