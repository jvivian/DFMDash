from functools import reduce

import pandas as pd
import pytest

from covid19_drdfm.processing import (
    DATA_DIR,
    ROOT_DIR,
    add_datetime,
    adjust_inflation,
    adjust_pandemic_response,
    get_df,
    get_govt_fund_dist,
)


@pytest.fixture
def raw_data() -> pd.DataFrame:
    with open(DATA_DIR / "df_paths.txt") as f:
        paths = [ROOT_DIR / x.strip() for x in f.readlines()]
    dfs = [pd.read_csv(x) for x in paths]
    return reduce(lambda x, y: pd.merge(x, y, on=["State", "Year", "Period"], how="left"), dfs).fillna(0)


# Fixture to load test data
@pytest.fixture
def sample_data() -> pd.DataFrame:
    return get_df()


def test_get_govt_fund_dist():
    govt_fund = get_govt_fund_dist()
    assert len(govt_fund) > 0, "File contains no values to use for distribution"
    assert int(sum(govt_fund) + 0.00001) == 1, "Distribution must sum to 1"


def test_adjust_inflation(sample_data):
    input_df = sample_data.copy()
    output_df = adjust_inflation(input_df)
    assert input_df.Demand_1.iloc[0] < output_df.Demand_1.iloc[0]


def test_adjust_pandemic_response(sample_data):
    input_df = sample_data.copy()
    #! Note - this is testing functionality, but is used per-state not on whole df
    out = adjust_pandemic_response(input_df)
    df = get_df()
    responses = [f"Pandemic_Response_{x}" for x in [13, 14, 15]]
    for r in responses:
        assert df[r].sum() == out[r].sum()


def test_fix_datetime(raw_data):
    input_df = raw_data.copy()
    output_df = add_datetime(input_df)
    assert isinstance(output_df["Time"][0], pd.Timestamp)


def test_run():
    df = get_df()
    expected_columns = ["State", "Supply_1", "Demand_1", "Pandemic_Response_13", "Time"]
    assert all(col in df.columns for col in expected_columns)


if __name__ == "__main__":
    pytest.main()
