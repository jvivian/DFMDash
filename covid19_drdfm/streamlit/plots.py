import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

from covid19_drdfm.constants import FACTORS


def plot_correlations(df: pd.DataFrame, normalize=False) -> None:
    """
    Plots the correlations between variables in the given DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the variables.

    Returns:
    None
    """
    factors = FACTORS.copy()
    var_df = pd.Series(df.drop(columns=["State", "Time"]).columns, name="Variables").to_frame()
    var_df["Group"] = [factors[x][1] for x in var_df.Variables if x in df.columns]
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    c5, c6 = st.columns(2)
    for group, stcol in zip(var_df.Group.unique(), [c1, c2, c3, c4, c5, c6]):
        cols = var_df[var_df.Group == group].Variables
        new = pd.DataFrame(MinMaxScaler().fit_transform(df[cols]), columns=cols) if normalize else df[cols]
        corr = px.imshow(
            new.fillna(0).corr(),
            zmin=-1,
            zmax=1,
            color_continuous_scale="rdbu_r",
            color_continuous_midpoint=0,
        )
        stcol.subheader(group)
        stcol.plotly_chart(corr)
