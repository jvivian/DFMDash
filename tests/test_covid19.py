import pandas as pd
from anndata import AnnData

from covid19_drdfm.covid19 import (
    _get_raw_df,
    get_raw,
    get_df,
    get_project_h5ad,
    get_govt_fund_dist,
    adjust_inflation,
    adjust_pandemic_response,
    add_datetime,
    fix_names,
)


def test_get_raw():
    raw_df = get_raw()
    assert isinstance(raw_df, pd.DataFrame)


def test_get_df():
    df = get_df()
    assert isinstance(df, pd.DataFrame)


def test_get_project_h5ad():
    project_h5ad = get_project_h5ad()
    assert isinstance(project_h5ad, AnnData)


def test_get_govt_fund_dist():
    govt_fund_dist = get_govt_fund_dist()
    assert isinstance(govt_fund_dist, list)
    assert all(isinstance(value, float) for value in govt_fund_dist)


def test_adjust_inflation():
    df = get_raw()
    adjusted_df = adjust_inflation(df)
    assert isinstance(adjusted_df, pd.DataFrame)


def test_adjust_pandemic_response():
    df = get_raw()
    adjusted_df = adjust_pandemic_response(df)
    assert isinstance(adjusted_df, pd.DataFrame)


def test_add_datetime():
    df = _get_raw_df()
    df_with_datetime = add_datetime(df)
    assert isinstance(df_with_datetime["Time"], pd.Series)
    assert isinstance(df_with_datetime, pd.DataFrame)


def test_fix_names():
    df = _get_raw_df()
    df_fixed_names = fix_names(df)
    assert not df.columns.equals(df_fixed_names.columns)
    assert isinstance(df_fixed_names, pd.DataFrame)
