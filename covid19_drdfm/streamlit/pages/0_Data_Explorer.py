from functools import reduce
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.io as pio
import plotly_express as px
from sklearn.preprocessing import MinMaxScaler
import streamlit as st

from covid19_drdfm.constants import DIFF_COLS, FACTORS_GROUPED, LOG_DIFF_COLS
from covid19_drdfm.covid19 import add_datetime, adjust_inflation, fix_names, adjust_pandemic_response
from covid19_drdfm.streamlit.plots import plot_correlations

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"

ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
DATA_DIR = ROOT_DIR / "data/processed"


@st.cache_data
def raw_data():
    with open(DATA_DIR / "df_paths.txt") as f:
        paths = [ROOT_DIR / x.strip() for x in f.readlines()]
    dfs = [pd.read_csv(x) for x in paths]
    return (
        reduce(lambda x, y: pd.merge(x, y, on=["State", "Year", "Period"], how="left"), dfs)
        .drop(columns=["Monetary_1_x", "Monetary_11_x"])
        .rename(columns={"Monetary_1_y": "Monetary_1", "Monetary_11_y": "Monetary_11"})
        .drop(columns=["Proportion", "proportion_vax2", "Pandemic_Response_8", "Distributed"])
        .pipe(fix_names)
        .pipe(add_datetime)
        .pipe(adjust_inflation)
        .pipe(adjust_pandemic_response)
    )


@st.cache_data
def process_data(raw_data: pd.DataFrame, state: str) -> pd.DataFrame:
    df = raw_data[raw_data.State == state]
    df[DIFF_COLS] = df[DIFF_COLS].diff() 
    df[LOG_DIFF_COLS] = df[LOG_DIFF_COLS].apply(lambda x: np.log(x + 1)).diff()
    return df.iloc[1:]

def normalize(df):
    index = df.index
    df = pd.DataFrame(MinMaxScaler().fit_transform(df), columns=df.columns)
    df.index = index
    return df


# Read in data
raw = raw_data()
# Parameters
state = st.sidebar.selectbox("Select State", sorted(raw["State"].unique()))
factor = st.sidebar.selectbox("Factor", sorted(FACTORS_GROUPED))
selections = ["Raw", "Processed", "Normalized"]
selection = st.sidebar.selectbox("Data Processing", selections)

# Specify dataframe based on user choice
proc = process_data(raw, state)
df = proc if selection == "Processed" else raw
df = normalize(proc).fillna(0) if selection == "Normalized" else df[df["State"] == state]

with st.expander(f"{selection} Dataframe"):
    st.dataframe(df)

# Tidy data
variables = FACTORS_GROUPED[factor] + ["Time"]
melt = df[variables].melt(
    id_vars=["Time"],
    var_name="Variable",
    value_name="Value",
)

# Create Plotly figure
fig = px.line(melt, x="Time", y="Value", color="Variable", title=f"{selection} Data of {factor} Factor Variables")
st.plotly_chart(fig, use_container_width=True)

# Display correlations for state
st.warning(f"Correlations are calculated using {selection} dataframe")
plot_correlations(df)
