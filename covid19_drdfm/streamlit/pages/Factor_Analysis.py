import streamlit as st
import json
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd
import plotly.io as pio
import plotly_express as px
import statsmodels.api as sm
import streamlit as st
from rich import print as pprint
from sklearn.preprocessing import MinMaxScaler

from covid19_drdfm.constants import FACTORS_GROUPED
from covid19_drdfm.dfm import state_process
from covid19_drdfm.processing import get_df, normalize


st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"


# Read in data
raw = get_df()
# TEST_DIR = Path('covid19_drdfm/data/example-output/')

# Parameter for results
path_to_results = Path(st.text_input("Path to results", value="./covid19_drdfm/data/example-output/"))
factor_path = path_to_results / "filtered-factors.csv"
df = pd.read_csv(factor_path)

# Selection parameters
factor = st.sidebar.selectbox("Factor", df.columns[2:-1])
state = st.sidebar.selectbox("State", df.State.unique())

# Grab first state to fetch valid variables
for state_subdir in path_to_results.iterdir():
    if not state_subdir.is_dir():
        continue
    valid_cols = pd.read_csv(state_subdir / "df.tsv", sep="\t").columns
    break
factor_vars = [x for x in FACTORS_GROUPED[factor] if x in valid_cols]
columns = [*factor_vars, "State", "Time"]

# Normalize original data for state / valid variables
new = normalize(raw.query("State == @state")[columns])

# Normalize factors and add to new dataframe
df["Time"] = new["Time"]
new[factor] = normalize(df)[factor]

# Melt into format for plotting
melted_df = new.drop(columns="State").melt(id_vars=["Time"], value_name="value")
melted_df["Label"] = [5 if x == factor else 1 for x in melted_df.variable]

# Plot
f = px.line(melted_df, x="Time", y="value", color="variable", hover_data="variable", line_dash="Label")
st.plotly_chart(f, use_container_width=True)
