"""
Handles I/O and processing of data into consolidated DataFrame object
"""
# %%
from functools import reduce
from pathlib import Path

import pandas as pd


def run() -> pd.DataFrame:
    """Run all processing steps as a series of `pipe`s

    Returns:
        pd.DataFrame: Processed DF
    """
    return get_df().pipe(adjust_inflation).pipe(fix_datetime)


def get_df() -> pd.DataFrame:
    """Read input DataFrames

    Returns:
        pd.DataFrame: Merged DataFrame from input DataFrames
    """
    path = Path(__file__).parent / "data/output/df_paths.txt"
    with open(path) as f:
        paths = [x.strip() for x in f.readlines()]
    dfs = [pd.read_csv(x) for x in paths]
    return reduce(lambda x, y: pd.merge(x, y, on=["State", "Year", "Period"], how="left"), dfs).fillna(0)


def adjust_inflation(df: pd.DataFrame) -> pd.DataFrame:
    """Processing `pipe`: Adjust for Inflation

    Args:
        df (pd.DataFrame): Input DF (see `get_df`)

    Returns:
        pd.DataFrame: Adjusted DF
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
    """I do not understand this

    Args:
        df (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    government_fund_dist_unif = {0: 1 / 6, 1: 1 / 6, 2: 1 / 6, 3: 1 / 6, 4: 1 / 6, 5: 1 / 6}
    for i in range(0, len(df)):
        if df.loc[i, "Pandemic_Response_13"] > 0:
            for n in range(0, len(government_fund_dist_unif)):
                df.loc[i + n, "Pandemic_Response_13"] = df.loc[i, "Pandemic_Response_13"] * government_fund_dist_unif[n]
            df.loc[i, "Pandemic_Response_13"] = df.loc[i, "Pandemic_Response_13"] * government_fund_dist_unif[0]
            break

    for i in range(0, len(df)):
        if df.loc[i, "Pandemic_Response_14"] > 0:
            for n in range(0, len(government_fund_dist_unif)):
                df.loc[i + n, "Pandemic_Response_14"] = df.loc[i, "Pandemic_Response_14"] * government_fund_dist_unif[n]
            df.loc[i, "Pandemic_Response_14"] = df.loc[i, "Pandemic_Response_14"] * government_fund_dist_unif[0]
            break

    for i in range(0, len(df)):
        if df.loc[i, "Pandemic_Response_15"] > 0:
            for n in range(0, len(government_fund_dist_unif)):
                df.loc[i + n, "Pandemic_Response_15"] = df.loc[i, "Pandemic_Response_15"] * government_fund_dist_unif[n]
            df.loc[i, "Pandemic_Response_15"] = df.loc[i, "Pandemic_Response_15"] * government_fund_dist_unif[0]
            break


def fix_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Sets `Time` column to `datetime` dtype

    Args:
        df (pd.DataFrame): Input DF

    Returns:
        pd.DataFrame: DType adjusted output
    """
    df = df.assign(Month=pd.to_numeric(df.Period.apply(lambda x: x[1:]))).assign(Day=1)
    df["Time"] = pd.to_datetime(year=df["Year"], month=df["Month"], day=df["Day"])
    return df.drop(columns=["Period", "Month", "Year", "Day"])


# %%
if __name__ == "__main__":  # pragma: no cover
    run()
    pass
