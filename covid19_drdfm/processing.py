# %%


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

# %%
def fix_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={'Cases1': 'Pandemic_1', 'Cases2': 'Pandemic_2',\
                            'Cases3': 'Pandemic_3', 'Cases4': 'Pandemic_4', \
                            'Cases5': 'Pandemic_5', 'Hosp1': 'Pandemic_6',\
                            'Hosp2': 'Pandemic_7', 'Deaths1': 'Pandemic_8', \
                            'Deaths2': 'Pandemic_9', 'Deaths3': 'Pandemic_10'\
                            'Deaths4': 'Pandemic_11', 'Deaths5': 'Pandemic_12'\
                            'Vax1': 'Pandemic_Response_1', 'Vax2': 'Pandemic_Response_2',\
                            'Vax3': 'Pandemic_Response_3', 'Gather1': 'Pandemic_Response_4', \
                            'Gather2': 'Pandemic_Response_5', 'Gather3': 'Pandemic_Response_6',\
                            'Gather4': 'Pandemic_Response_7', 'SaH': 'Pandemic_Response_8', \
                            'Curfew': 'Pandemic_Response_9', 'Mask1': 'Pandemic_Response_10'\
                            'Mask2': 'Pandemic_Response_11', 'School': 'Pandemic_Response_12'\
                            'Cons1': 'Demand_1', 'Cons2': 'Demand_2',\
                            'Cons3': 'Demand_3', 'Cons4': 'Demand_4',\
                            'Cons5': 'Demand_5', 'Employment1': 'Demand_6',\
                            'Employment2': 'Demand_7', 'GDP': 'Supply_1',\
                            'UI': 'Supply_2', 'PartR': 'Supply_3',\
                            'UR': 'Supply_4', 'RPFI': 'Supply_5',\
                            'FixAss': 'Supply_6', 'Prod': 'Supply_7',\
                            'CPI': 'Monetary_1', 'CPIU': 'Monetary_2',\
                            'PCE': 'Monetary_3', 'PCEC': 'Monetary_4',\
                            'TBill1mo': 'Monetary_5', 'TBill6mo': 'Monetary_6',\
                            'TBill1yr': 'Monetary_7', 'TBill5yr': 'Monetary_8',\
                            'TBill10yr': 'Monetary_9', 'TBill30yr': 'Monetary_10',\
                            'FFR': 'Monetary_11'})
    """
    #write the code that will change the dataframes names
    # Look at other pandemic functions
    # return modified version of the dataframe
    # Have test code to validate"""

def factordic()
    factors = {}
    factors[Cases1] = 'Global', 'Pandemic'
    factors[Cases2] = 'Global', 'Pandemic'
    factors[Cases3] = 'Global', 'Pandemic'
    factors[Cases4] = 'Global', 'Pandemic'
    factors[Cases5] = 'Global', 'Pandemic'
    factors[Hosp1] = 'Global', 'Pandemic'
    factors[Hosp2] = 'Global', 'Pandemic'
    factors[Deaths1] = 'Global', 'Pandemic'
    factors[Deaths2] = 'Global', 'Pandemic'
    factors[Deaths3] = 'Global', 'Pandemic'
    factors[Deaths4] = 'Global', 'Pandemic'
    factors[Deaths5] = 'Global', 'Pandemic'
    factors[Vax1] = 'Global', 'Response'
    factors[Vax2] = 'Global', 'Response'
    factors[Vax3] = 'Global', 'Response'
    factors[Gather1] = 'Global', 'Response'
    factors[Gather2] = 'Global', 'Response'
    factors[Gather3] = 'Global', 'Response'
    factors[Gather4] = 'Global', 'Response'
    factors[SaH] = 'Global', 'Response'
    factors[Curfew] = 'Global', 'Response'
    factors[Mask1] = 'Global', 'Response'
    factors[Mask2] = 'Global', 'Response'
    factors[School] = 'Global', 'Response'
    factors[Cons1] = 'Global', 'Consumption'
    factors[Cons2] = 'Global', 'Consumption'
    factors[Cons3] = 'Global', 'Consumption'
    factors[Cons4] = 'Global', 'Consumption'
    factors[Cons5] = 'Global', 'Consumption'
    factors[Employment1] = 'Global', 'Employment'
    factors[Employment2] = 'Global', 'Employment'
    factors[UI] = 'Global', 'Employment'
    factors[PartR] = 'Global', 'Employment'
    factors[UR] = 'Global', 'Employment'
    factors[CPI] = 'Global', 'Inflation'
    factors[CPIU] = 'Global', 'Inflation'
    factors[PCE] = 'Global', 'Inflation'
    factors[PCEC] = 'Global', 'Inflation'
    factors[RPFI] = 'Global', 'Uncat'
    factors[FixAss] = 'Global', 'Uncat'
    factors[Prod] = 'Global', 'Uncat'
    factors[GDP] = 'Global', 'Uncat'
    factors[TBill1mo] = 'Global', 'Uncat'
    factors[TBill6mo] = 'Global', 'Uncat'
    factors[TBill1yr] = 'Global', 'Uncat'
    factors[TBill5yr] = 'Global', 'Uncat'
    factors[TBill10tr] = 'Global', 'Uncat'
    factors[TBill30yr] = 'Global', 'Uncat'
    factors[TBillFFR] = 'Global', 'Uncat'



