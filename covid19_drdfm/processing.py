"""I/O and processing module

Converts all input files into single consolidated dataframe that can be used
downstream as model input

This model input DataFrame can be generated with a single function:
    - `df = run()`
"""
import json
from fractions import Fraction
from functools import reduce
from pathlib import Path

import fastparquet
import pandas as pd
import yaml

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
        # .assign(Pandemic_Response_4=lambda x: x[['Pandemic_Response_4', 'Pandemic_Response_5', 'Pandemic_Response_6', 'Pandemic_Response_7']].max(axis=1))
        # .assign(Pandemic_Response_10=lambda x: x[['Pandemic_Response_10', 'Pandemic_Response_11']].max(axis=1))
        # .drop(columns=['Pandemic_Response_5','Pandemic_Response_6', 'Pandemic_Response_7', 'Pandemic_Response_11'])
        .pipe(adjust_inflation)
        .pipe(add_datetime)
    )


def get_factors() -> dict[str, (str, str)]:
    """Fetch pre-defined factors for model

    Returns:
        dict[str, (str, str)]: Factors from `./data/processed/factors.yaml`
    """
    with open(DATA_DIR / "factors.json") as f:
        return json.load(f)


def write(df: pd.DataFrame, outpath: Path) -> Path:
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
    responses = [f"Pandemic_Response_{x}" for x in [13, 14, 15]]
    for r in responses:
        df[r] = df[r].astype(float)
        i = df.index[df[r] > 0][0]
        fund = df.loc[i, r]
        for n in range(0, len(govt_fund_dist)):
            df.loc[i + n, r] = fund * govt_fund_dist[n]
    return df


def add_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Sets `Time` column to `DateTime` dtype

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: DType adjusted DataFrame
    """
    df = df.assign(Month=pd.to_numeric(df.Period.apply(lambda x: x[1:]))).assign(Day=1)
    df["Time"] = pd.to_datetime({"year": df.Year, "month": df.Month, "day": df.Day})
    return df.drop(columns=["Period", "Month", "Year", "Day"])
