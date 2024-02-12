# Raw
# Post-processed
# Normalized

from functools import reduce
from pathlib import Path

import pandas as pd
import plotly.io as pio
import plotly_express as px
import streamlit as st

from covid19_drdfm.constants import DIFF_COLS, LOG_DIFF_COLS, FACTORS_GROUPED
from covid19_drdfm.processing import (
    add_datetime,
    adjust_inflation,
    adjust_pandemic_response,
    diff_vars,
    fix_names,
    normalize,
)
from covid19_drdfm.dfm import state_process

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
        .pipe(adjust_pandemic_response)
    )


@st.cache_data
def processed_data(raw_data: pd.DataFrame, state: str) -> pd.DataFrame:
    return (
        raw_data[raw_data.State == state]
        .pipe(diff_vars, cols=DIFF_COLS)
        .pipe(diff_vars, cols=LOG_DIFF_COLS, log=True)
        .iloc[1:]
    )


# Read in data
raw = raw_data()
# Parameters
state = st.sidebar.selectbox("Select State", sorted(raw["State"].unique()))
factor = st.sidebar.selectbox("Factor", sorted(FACTORS_GROUPED))
selections = ["Raw", "Processed", "Normalized"]
selection = st.sidebar.selectbox("Data Processing", selections)

proc = processed_data(raw, state)

# Filter DataFrame based on user inputs
# df_filtered = raw[(raw["State"] == state) & (raw["Time"].between(time_range[0], time_range[1]))]

# Show normalized if so
df = proc if selection == "Processed" else raw

with st.expander("Raw Data"):
    st.dataframe(raw[raw.State == state])

with st.expander("Processed Data"):
    st.dataframe(proc)

with st.expander("Normalized"):
    norm = normalize(proc).fillna(0)
    st.dataframe(norm)

df = norm if selection == "Normalized" else df[df["State"] == state]

variables = FACTORS_GROUPED[factor] + ["Time"]

melt = df[variables].melt(
    id_vars=["Time"],
    var_name="Variable",
    value_name="Value",
)

# Create Plotly figure
fig = px.line(melt, x="Time", y="Value", color="Variable")  # replace y with your variable column

# Display Plotly figure in Streamlit
st.plotly_chart(fig, use_container_width=True)
