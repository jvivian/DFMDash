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
        .pipe(adjust_inflation)
        .pipe(add_datetime)
        .pipe(fix_names)
    )


# def get_factors() -> dict[str, (str, str)]:
#     """Fetch pre-defined factors for model

#     Returns:
#         dict[str, (str, str)]: Factors from `./data/processed/factors.yaml`
#     """
#     with open(DATA_DIR / "factors.json") as f:
#         return json.load(f)


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


def fix_names(df: pd.DataFrame) -> pd.DataFrame:
    """Map sensible names to the merged input dataframe

    Args:
        df (pd.DataFrame): Input DataFrame after merging all input data

    Returns:
        pd.DataFrame: DataFrame with mapped names
    """
    return df.rename(
        columns={
            "Pandemic_1": "Cases1",
            "Pandemic_2": "Cases2",
            "Pandemic_3": "Cases3",
            "Pandemic_4": "Cases4",
            "Pandemic_5": "Cases5",
            "Pandemic_6": "Hosp1",
            "Pandemic_7": "Hosp2",
            "Pandemic_8": "Deaths1",
            "Pandemic_9": "Deaths2",
            "Pandemic_10": "Deaths3",
            "Pandemic_11": "Deaths4",
            "Pandemic_12": "Deaths5",
            "Pandemic_Response_1": "Vax1",
            "Pandemic_Response_2": "Vax2",
            "Pandemic_Response_3": "Vax3",
            "Pandemic_Response_4": "Gather1",
            "Pandemic_Response_5": "Gather2",
            "Pandemic_Response_6": "Gather3",
            "Pandemic_Response_7": "Gather4",
            "Pandemic_Response_8": "SaH",
            "Pandemic_Response_9": "Curfew",
            "Pandemic_Response_10": "Mask1",
            "Pandemic_Response_11": "Mask2",
            "Pandemic_Response_12": "School",
            "Pandemic_Response_13": "ARP",
            "Pandemic_Response_14": "PPP",
            "Pandemic_Response_15": "CARES",
            "Demand_1": "Cons1",
            "Demand_2": "Cons2",
            "Demand_3": "Cons3",
            "Demand_4": "Cons4",
            "Demand_5": "Cons5",
            "Demand_6": "Employment1",
            "Demand_7": "Employment2",
            "Supply_1": "GDP",
            "Supply_2": "UI",
            "Supply_3": "PartR",
            "Supply_4": "UR",
            "Supply_5": "RPFI",
            "Supply_6": "FixAss",
            "Supply_7": "Prod",
            "Monetary_1": "CPI",
            "Monetary_2": "CPIU",
            "Monetary_3": "PCE",
            "Monetary_4": "PCEC",
            "Monetary_5": "TBill1mo",
            "Monetary_6": "TBill6mo",
            "Monetary_7": "TBill1yr",
            "Monetary_8": "TBill5yr",
            "Monetary_9": "TBill10yr",
            "Monetary_10": "TBill30yr",
            "Monetary_11": "FFR",
        }
    )


def get_factors():
    """Returns the pre-assigned factors for the model"""
    return {
        "Cases1": ("Global", "Pandemic"),
        "Cases2": ("Global", "Pandemic"),
        "Cases3": ("Global", "Pandemic"),
        "Cases4": ("Global", "Pandemic"),
        "Cases5": ("Global", "Pandemic"),
        "Hosp1": ("Global", "Pandemic"),
        "Hosp2": ("Global", "Pandemic"),
        "Deaths1": ("Global", "Pandemic"),
        "Deaths2": ("Global", "Pandemic"),
        "Deaths3": ("Global", "Pandemic"),
        "Deaths4": ("Global", "Pandemic"),
        "Deaths5": ("Global", "Pandemic"),
        "Vax1": ("Global", "Response"),
        "Vax2": ("Global", "Response"),
        "Vax3": ("Global", "Response"),
        "Gather1": ("Global", "Response"),
        "Gather2": ("Global", "Response"),
        "Gather3": ("Global", "Response"),
        "Gather4": ("Global", "Response"),
        "SaH": ("Global", "Response"),
        "Curfew": ("Global", "Response"),
        "Mask1": ("Global", "Response"),
        "Mask2": ("Global", "Response"),
        "School": ("Global", "Response"),
        "ARP": ("Global", "Response"),
        "PPP": ("Global", "Response"),
        "CARES": ("Global", "Response"),
        "School": ("Global", "Response"),
        "School": ("Global", "Response"),
        "Cons1": ("Global", "Consumption"),
        "Cons2": ("Global", "Consumption"),
        "Cons3": ("Global", "Consumption"),
        "Cons4": ("Global", "Consumption"),
        "Cons5": ("Global", "Consumption"),
        "Employment1": ("Global", "Employment"),
        "Employment2": ("Global", "Employment"),
        "UI": ("Global", "Employment"),
        "PartR": ("Global", "Employment"),
        "UR": ("Global", "Employment"),
        "CPI": ("Global", "Inflation"),
        "CPIU": ("Global", "Inflation"),
        "PCE": ("Global", "Inflation"),
        "PCEC": ("Global", "Inflation"),
        "RPFI": ("Global", "Uncat"),
        "FixAss": ("Global", "Uncat"),
        "Prod": ("Global", "Uncat"),
        "GDP": ("Global", "Uncat"),
        "TBill1mo": ("Global", "Uncat"),
        "TBill6mo": ("Global", "Uncat"),
        "TBill1yr": ("Global", "Uncat"),
        "TBill5yr": ("Global", "Uncat"),
        "TBill10yr": ("Global", "Uncat"),
        "TBill30yr": ("Global", "Uncat"),
        "FFR": ("Global", "Uncat"),
    }
"""
Diff
        "Cases1"
        "Cases2"
        "Cases3"
        "Cases4"
        "Cases5"
        "Hosp1"
        "Hosp2"
        "Deaths1"
        "Deaths2"
        "Deaths3"
        "Deaths4"
        "Deaths5"

Log-Diff
        "Cons1"
        "Cons2"
        "Cons3"
        "Cons4"
        "Cons5"
        "Employment1"
        "Employment2"
        "CPI"
        "CPIU"
        "PCE"
        "PCEC"
        "RPFI"
        "FixAss"
        "Prod"
        "GDP"

Nothing

 Everything Else
 
 """