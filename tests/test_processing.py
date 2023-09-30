import pandas as pd
import pytest

from covid19_drdfm.processing import (
    add_datetime,
    adjust_inflation,
    adjust_pandemic_response,
    get_df,
    get_govt_fund_dist,
    run,
)


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
    pre_13 = input_df["Pandemic_Response_13"].sum()
    pre_14 = input_df["Pandemic_Response_14"].sum()
    pre_15 = input_df["Pandemic_Response_15"].sum()
    output_df = adjust_pandemic_response(input_df)
    assert pre_13 > output_df["Pandemic_Response_13"].sum()
    assert pre_14 > output_df["Pandemic_Response_14"].sum()
    assert pre_15 > output_df["Pandemic_Response_15"].sum()


def test_fix_datetime(sample_data):
    input_df = sample_data.copy()
    output_df = add_datetime(input_df)
    assert isinstance(output_df["Time"][0], pd.Timestamp)


def test_run():
    df = run()
    expected_columns = ["State", "Supply_1", "Demand_1", "Pandemic_Response_13", "Time"]
    assert all(col in df.columns for col in expected_columns)


if __name__ == "__main__":
    pytest.main()
