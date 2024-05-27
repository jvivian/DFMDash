import json
import time
from pathlib import Path

import pandas as pd
import plotly.io as pio
import streamlit as st

from covid19_drdfm.constants import FACTORS
from covid19_drdfm.covid19 import get_df, get_project_h5ad
from covid19_drdfm.dfm import ModelRunner
from covid19_drdfm.streamlit.plots import plot_correlations

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


@st.cache_data
def get_data():
    return get_df()


ad = get_project_h5ad()
factors = FACTORS.copy()
factor_vars = list(factors.keys())
var_df = ad.var
var_df["Group"] = var_df["factor"]
var_df["Variables"] = var_df.index
ad.obs["Time"] = pd.to_datetime(ad.obs.index)

center_title("Dynamic Factor Model Runner")

with st.expander("Variable correlations"):
    st.write("Data is normalized between [0, 1] before calculating correlation")
    plot_correlations(ad.to_df(), var_df, normalize=True)

with st.form("DFM Model Runner"):
    st.markdown(
        """
        <style>
            .stMultiSelect [data-baseweb=select] span{
                max-width: 250px;
                font-size: 0.9;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Parameters
    st.subheader("Factor/Variable Selection")
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    c5, c6 = st.columns(2)
    selectors = {}
    for group, stcol in zip(var_df.Group.unique(), [c1, c2, c3, c4, c5, c6]):
        variables = var_df[var_df.Group == group].Variables
        selectors[group] = stcol.multiselect(group, variables, variables)

    st.subheader("Batch Variable")
    states = sorted(ad.obs.State.unique())
    state_sel = st.multiselect("States", states, default=states)

    st.subheader("Parameters")
    c1, c2, c3, c4 = st.columns([0.35, 0.25, 0.20, 0.20])
    outdir = c1.text_input("Output Directory", value="./")
    min_val = ad.obs.Time.min()
    date_start = c2.date_input("Start Date", value=min_val, min_value=min_val, max_value=ad.obs.Time.max())
    mult_sel = c3.slider("Global Multiplier", 0, 4, 2)
    maxiter = c4.slider("Max EM Iterations", 1000, 20_000, 10_000, 100)
    ad = ad[ad.obs.index > date_start.isoformat()]

    # Transforms
    st.subheader("Transforms")
    c1, c2 = st.columns(2)
    c1.multiselect("Difference", ad.var.index, default=ad.var[ad.var["difference"]].index.to_list())
    c2.multiselect("LogDifference", ad.var.index, default=ad.var[ad.var["logdiff"]].index.to_list())

    # Variable Metadata
    with st.expander("Variable Metadata"):
        _, c, _ = st.columns([0.25, 0.5, 0.25])
        c.dataframe(ad.var)

    # Metrics
    st.subheader("Run Information")
    lengths = [len(selectors[x]) for x in selectors]
    num_groups = sum(1 for x in lengths if x != 0)
    _, f1, f2, _ = st.columns([0.25, 0.25, 0.25, 0.25])
    f1.metric("# Factor Groups", num_groups)
    f2.metric("# Variables", sum([len(selectors[x]) for x in selectors]))

    submitted = st.form_submit_button()

if not submitted:
    st.stop()


start = time.time()
_, c, _ = st.columns([0.3, 0.4, 0.3])
c.write("Creating output directory and starting model run(s)")
columns = []
for x in [x for x in selectors if selectors[x]]:
    columns.extend(selectors[x])
selectors.update({"global_multiplier": mult_sel, "outdir": outdir})
outdir = Path(outdir)
outdir.mkdir(exist_ok=True)
with open(outdir / "log.txt", "w") as f:
    json.dump(selectors, f)

# Run model for subset of states using batch mode
# TODO: No per-batch update sucks, try and fix during dynamic refactor
n = len(state_sel)
ad = ad[ad.obs.State.isin(state_sel)]
with st.spinner(f"Running {n} models..."):
    model = ModelRunner(ad, outdir=outdir, batch="State")
    model.run(maxiter=maxiter, global_multiplier=mult_sel, columns=columns)


# Combine filtered output
filt_paths = [subdir / "factors.csv" for subdir in outdir.iterdir() if (subdir / "factors.csv").exists()]
dfs = [pd.read_csv(x) for x in filt_paths]
try:
    filt_df = pd.concat([x for x in dfs if ~x.empty]).set_index("Time")
    filt_df.to_csv(outdir / "factors.csv")
    st.dataframe(filt_df)
    # model.ad.write(outdir / "data.h5ad")
    st.balloons()
except ValueError:
    st.error(f"No runs succeeded!! Check failures.txt in {outdir}")


end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)
st.write(f"Runtime: {int(hours):0>2}H:{int(minutes):0>2}M:{seconds:05.2f}S")
