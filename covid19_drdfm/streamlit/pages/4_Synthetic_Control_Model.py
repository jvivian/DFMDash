from pathlib import Path
import matplotlib.pyplot as plt

import seaborn as sns
import plotly.express as px
import anndata as ann
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from SyntheticControlMethods import DiffSynth, Synth
from datetime import datetime

from covid19_drdfm.constants import FACTORS_GROUPED
from covid19_drdfm.covid19 import get_df, get_project_h5ad

st.set_page_config(layout="wide")
pio.templates.default = "plotly_dark"

EX_PATH = Path("./covid19_drdfm/data/example-data/pandemic-only")


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


@st.cache_data()
def get_results(df, outcome_var, treatment_time, treated_unit):
    return Synth(df, outcome_var, "State", "Time", str(treatment_time), treated_unit, n_optim=10, pen="auto")


center_title("Synthetic Control Model Runner")


# DATA SELECTION
result_dir = Path(st.text_input("Result Directory", value=EX_PATH))
factors_path = result_dir / "factors.csv"

fdf = pd.read_csv(factors_path)
cols_to_drop = [x for x in fdf.columns if "Time." in x]
fdf = fdf.drop(columns=cols_to_drop)
fdf.columns = [x.lstrip("Factor_") for x in fdf.columns]

# Process Data
dfs = []
for subdir in result_dir.iterdir():
    if not subdir.is_dir():
        continue
    state = pd.read_csv(subdir / "df.csv")
    state["State"] = subdir.stem
    dfs.append(state)
df = pd.concat(dfs)
df = df.set_index(["Time", "State"])
columns = [x for x in fdf.columns if x not in df.columns]
min_time = pd.to_datetime(fdf["Time"]).min()
max_time = pd.to_datetime(fdf["Time"].max())
states = sorted(fdf.State.unique())
fdf = fdf[columns].set_index(["Time", "State"])
df = df.join(fdf)
with st.expander("Input Data"):
    st.dataframe(df)


# Select Variables
with st.form(key="scm"):
    treated_unit = st.selectbox("Treated Unit", states)
    predictor_vars = st.multiselect("Predictor Variables", df.columns, df.columns.to_list())
    outcome_var = st.selectbox("Outcome Variable", df.columns)
    treatment_time = st.date_input("Treatment Time", value=min_time, min_value=min_time, max_value=max_time)

    submit = st.form_submit_button()

if not submit:
    st.stop()


df = df[[*predictor_vars, outcome_var]].reset_index()
with st.expander("SCM Model Input"):
    st.dataframe(df)
with st.spinner("Synthetic Control Model Running..."):
    sc = get_results(df, outcome_var, treatment_time, treated_unit)
st.balloons()

st.divider()

st.subheader("Results")
with st.expander("Weight Vector"):
    st.dataframe(sc.original_data.weight_df)
with st.expander("Comparison Matrix"):
    st.dataframe(sc.original_data.comparison_df)
    st.write(f"PEN: {sc.original_data.pen}")


data = sc.original_data
synth = data.synth_outcome
treated_outcome_all = data.treated_outcome_all
treatment_period = data.treatment_period
treated_label = "Treated"
synth_label = "Synthetic Control"
treatment_label = "Treatment"

# Determine appropriate limits for y-axis
max_value = max(np.max(treated_outcome_all), np.max(synth))
min_value = min(np.min(treated_outcome_all), np.min(synth))

# Create x/y
x = df[df.State == treated_unit].Time
ys = synth[0, :]
y = df[df.State == treated_unit][outcome_var]

st.subheader("Original")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=f"{treated_unit} {outcome_var}"))
fig.add_trace(go.Scatter(x=x, y=ys, mode="lines", name=f"Synthetic {outcome_var}", line=dict(dash="dot")))
fig.add_vline(treatment_time, name=f"{outcome_var} Response")

# Display the combined plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

st.subheader("Pointwise")
normalized_treated_outcome = data.treated_outcome_all - ys.reshape(-1, 1)
normalized_treated_outcome = normalized_treated_outcome[:, 0]
normalized_synth = np.zeros(data.periods_all)
most_extreme_value = np.max(np.absolute(normalized_treated_outcome))
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=normalized_treated_outcome, mode="lines", name=f"Synthetic {outcome_var}"))
fig.add_trace(
    go.Scatter(x=x, y=normalized_synth, mode="lines", name=f"{treated_unit} {outcome_var}", line=dict(dash="dot"))
)
fig.add_vline(treatment_time, name=f"{outcome_var} Response")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Cumulative")
cumulative_effect = np.cumsum(normalized_treated_outcome[data.periods_pre_treatment :])
cummulative_treated_outcome = np.concatenate((np.zeros(data.periods_pre_treatment), cumulative_effect), axis=None)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=normalized_synth, mode="lines", name=f"Synthetic {outcome_var}", line=dict(dash="dot")))
fig.add_trace(go.Scatter(x=x, y=cummulative_treated_outcome, mode="lines", name=f"{treated_unit} {outcome_var}"))
fig.add_vline(treatment_time, name=f"{outcome_var} Response")
st.plotly_chart(fig, use_container_width=True)
