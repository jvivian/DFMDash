import pandas as pd
import pytest
from src.processing import (
    adjust_inflation,
    adjust_pandemic_response,
    fix_datetime,
    get_df,
    get_govt_fund_dist,
    run,
)


# Define a fixture to load test data
@pytest.fixture
def sample_data() -> pd.DataFrame:
    # Replace with your test data or loading logic
    # data = {
    #     "State": ["AK", "AK", "AK", "AK", "AK"],
    #     "Supply_1": [59188.506187, 58911.647998, 58654.835314, 58629.129704, 58746.249103],
    #     # Add more columns as needed
    # }
    # return pd.DataFrame(data)
    return get_df()


def test_get_govt_fund_dist():
    govt_fund = get_govt_fund_dist()
    assert len(govt_fund) > 0, "File contains no values to use for distribution"
    assert sum(govt_fund) == 1, "Distribution must sum to 1"


# Test the adjust_inflation function
def test_adjust_inflation(sample_data):
    input_df = sample_data.copy()
    output_df = adjust_inflation(input_df)

    # Add assertions to check the correctness of the adjustments
    assert (output_df["Demand_1"] == input_df["Demand_1"] / (input_df["Monetary_3"] / 100)).all()
    # Add more assertions for other columns as needed


# Test the adjust_pandemic_response function
def test_adjust_pandemic_response(sample_data):
    input_df = sample_data.copy()
    output_df = adjust_pandemic_response(input_df)

    # Add assertions to check the correctness of the adjustments
    # For example, check if the values in "Pandemic_Response_X" columns are adjusted correctly
    assert output_df["Pandemic_Response_13"].equals(input_df["Pandemic_Response_13"] * 0.08)
    # Add more assertions for other columns as needed


# Test the fix_datetime function
def test_fix_datetime(sample_data):
    input_df = sample_data.copy()
    output_df = fix_datetime(input_df)

    # Add assertions to check the correctness of the datetime adjustments
    # For example, check if the "Time" column is of datetime dtype
    assert isinstance(output_df["Time"][0], pd.Timestamp)
    # Add more assertions for other datetime-related checks


# Test the run function
def test_run(sample_data):
    input_df = sample_data.copy()
    output_df = run(input_df)

    # Add assertions to check the correctness of the entire processing pipeline
    # For example, check if the output DataFrame has the expected columns
    expected_columns = ["State", "Supply_1", "Demand_1", "Pandemic_Response_13", "Time"]
    assert all(col in output_df.columns for col in expected_columns)
    # Add more assertions as needed


# # Add more test functions as needed for other parts of your module

# if __name__ == "__main__":
#     pytest.main()
