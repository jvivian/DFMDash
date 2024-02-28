from pathlib import Path

import pandas as pd
import plotly.io as pio
import plotly_express as px
import streamlit as st

from covid19_drdfm.constants import FACTORS_GROUPED
from covid19_drdfm.processing import get_df, normalize

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"


# Read in data
raw = get_df()
# TEST_DIR = Path('covid19_drdfm/data/example-output/')

# Parameter for results
path_to_results = Path(st.text_input("Path to results", value="./covid19_drdfm/data/example-data"))
factor_path = path_to_results / "filtered-factors.csv"
df = pd.read_csv(factor_path, index_col=0)
df["Time"] = df.index
df.index.name = "Time"

filter_list = ["Unnamed", "Time", "State"]
factor = st.sidebar.selectbox("Factor", [x for x in df.columns if x not in filter_list and "Global" not in x])
state = st.sidebar.selectbox("State", sorted(df.State.unique()))

with st.expander("State Factors"):
    st.dataframe(df)

# Grab first state to fetch valid variables
for state_subdir in path_to_results.iterdir():
    if not state_subdir.is_dir():
        continue
    valid_cols = pd.read_csv(state_subdir / "df.tsv", sep="\t").columns
    # valid_cols = [x for x in valid_cols i]
    break
factor_vars = [x for x in FACTORS_GROUPED[factor] if x in valid_cols]
columns = [*factor_vars, "State", "Time"]

# Normalize original data for state / valid variables
raw = raw.set_index("Time", drop=False)
new = normalize(raw[raw.State == state][columns]).set_index("Time", drop=False)

# Normalize factors and add to new dataframe
if st.sidebar.checkbox("Invert Factor"):
    df[factor] = df[factor] * -1
df = normalize(df[df.State == state]).set_index("Time", drop=False)  # .reset_index(drop=True)
new = new.loc[df.index, :]
new[factor] = list(df[factor])

# Melt into format for plotting
melted_df = new.drop(columns="State").melt(id_vars=["Time"], value_name="value")
melted_df["Label"] = [5 if x == factor else 1 for x in melted_df.variable]

# Plot
f = px.line(melted_df, x="Time", y="value", color="variable", hover_data="variable", line_dash="Label")
st.plotly_chart(f, use_container_width=True)

# Model Results
results_path = path_to_results / state / "results.csv"
model_path = path_to_results / state / "model.csv"

values = pd.Series()
with open(results_path) as f:
    for line in f.readlines():
        if "AIC" in line:
            values["AIC"] = float(line.strip().split(",")[-1])
        elif "Log Likelihood" in line:
            values["LogLikelihood"] = float(line.strip().split(",")[-1])
        elif "EM" in line:
            values["EM Iterations"] = float(line.strip().split(",")[-1])

_, c1, c2, c3, _ = st.columns(5)
help_msgs = ["LogLikelihood: Higher is better", "AIC: Lower is better", "Number of steps to convergence"]
for val, col, msg in zip(values.index, [c1, c2, c3], help_msgs):
    col.metric(val, values[val], help=msg)

# TODO: Plot values against distribution of (i.e. against AIC for all states)
