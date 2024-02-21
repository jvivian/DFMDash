import json
import time
from pathlib import Path

import pandas as pd
import plotly.io as pio
import plotly_express as px
import statsmodels.api as sm
import streamlit as st
from rich import print as pprint
from sklearn.preprocessing import MinMaxScaler

from covid19_drdfm.constants import FACTORS
from covid19_drdfm.dfm import run_parameterized_model
from covid19_drdfm.processing import get_df

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


@st.cache_data
def get_data():
    return get_df()


df = get_df()
sub = pd.Series([x for x in df.columns if x not in ["State", "Time"]], name="Variables").to_frame()
factors = FACTORS.copy()
factor_vars = list(factors.keys())
sub["Group"] = [factors[x][1] for x in sub.Variables if x in df.columns]

center_title("Dynamic Factor Model Runner")

with st.expander("Variable correlations"):
    st.write("Data is normalized between [0, 1] before calculating correlation")
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    c5, c6 = st.columns(2)
    for group, stcol in zip(sub.Group.unique(), [c1, c2, c3, c4, c5, c6]):
        cols = sub[sub.Group == group].Variables
        corr = px.imshow(
            pd.DataFrame(MinMaxScaler().fit_transform(df[cols]), columns=cols).corr(),
            zmin=-1,
            zmax=1,
            color_continuous_scale="rdbu_r",
            color_continuous_midpoint=0,
        )
        stcol.subheader(group)
        stcol.plotly_chart(corr)


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
    # Variable selections
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    c5, c6 = st.columns(2)
    selectors = {}
    for group, stcol in zip(sub.Group.unique(), [c1, c2, c3, c4, c5, c6]):
        variables = sub[sub.Group == group].Variables
        selectors[group] = stcol.multiselect(group, variables, variables)

    # State selections
    state_sel = st.multiselect("States", df.State.unique(), default=df.State.unique())
    c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
    outdir = c1.text_input("Output Directory", value="./")
    mult_sel = c2.slider("Global Multiplier", 0, 4, 2)
    maxiter = c3.slider("Max EM Iterations", 1000, 20_000, 10_000, 100)

    # Metrics
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


progress_text = "Running model on designated states..."
my_bar = c.progress(0, text=progress_text)

n = len(state_sel)
_ = [factors.pop(x) for x in factor_vars if x not in df.columns]
for i, state in enumerate(state_sel):
    _ = run_parameterized_model(
        df, state, outdir, columns=columns, factors=factors, global_multiplier=mult_sel, maxiter=maxiter
    )
    my_bar.progress((i + 1) / n, text=progress_text)

my_bar.empty()
filt_paths = [
    subdir / "filtered-factors.csv" for subdir in outdir.iterdir() if (subdir / "filtered-factors.csv").exists()
]
dfs = [pd.read_csv(x) for x in filt_paths]
try:
    filt_df = pd.concat([x for x in dfs if ~x.empty]).set_index("Time")
except ValueError:
    filt_df = pd.DataFrame()
filt_df.to_csv(outdir / "filtered-factors.csv")
st.dataframe(filt_df)

end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)
st.write(f"Runtime: {int(hours):0>2}H:{int(minutes):0>2}M:{seconds:05.2f}S")

fail_path = outdir / "failed.txt"
if fail_path.exists():
    with open(fail_path) as f:
        lines = f.readlines()
    _, c1, c2, _ = st.columns([0.1, 0.2, 0.6, 0.1])
    c1.metric("Failures", value=len(lines))
    lines = "\n".join(lines)
    c2.warning(f"\t\tFailures Detected\n\n{lines}")

st.balloons()
