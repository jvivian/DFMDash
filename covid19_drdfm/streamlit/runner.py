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

from covid19_drdfm.dfm import state_process
from covid19_drdfm.processing import get_df, get_factors

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"

DEFAULTS = {
    "Uncat": ["Monetary_5", "Monetary_9", "Monetary_10", "Supply_1", "Supply_7"],
    "Consumption": ["Demand_3", "Demand_4", "Demand_5"],
    "Response": [
        "Pandemic_Response_1",
        "Pandemic_Response_3",
        "Pandemic_Response_4",
        "Pandemic_Response_9",
        "Pandemic_Response_10",
        "Pandemic_Response_12",
    ],
    "Employment": ["Supply_2", "Supply_3", "Supply_4", "Demand_7"],
    "Inflation": ["Monetary_2", "Monetary_3", "Monetary_1"],
    "Pandemic": ["Pandemic_1", "Pandemic_2", "Pandemic_6", "Pandemic_9", "Pandemic_7", "Pandemic_10"],
}


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


def run_parameterized_model(
    df: pd.DataFrame, state: str, outdir: Path, columns: list[str], global_multiplier: int = 2
) -> sm.tsa.DynamicFactor:
    """Run DFM for a given state

    Args:
        df (pd.DataFrame): DataFrame processed via `covid19_drdfm.run`
        state (str): Two-letter state code to process
        outdir (str): Output directory for model CSV files

    Returns:
        sm.tsa.DynamicFactor: Dynamic Factor Model

    """
    # Factors and input data
    factors = get_factors()
    factor_multiplicities = {"Global": global_multiplier}
    df = state_process(df, state)
    columns = list(columns) + ["State", "Time"]
    columns = [x for x in columns if x in df.columns]
    new = df[columns]
    variables = list(factors.keys())
    _ = [factors.pop(var) for var in variables if var not in columns]
    # Save input data
    outdir.mkdir(exist_ok=True)
    out = outdir / state
    # pprint(f"Saving state input information to {out}")
    out.mkdir(exist_ok=True)
    new.to_excel(out / "df.xlsx")
    new.to_csv(out / "df.tsv", sep="\t")
    # Run Model
    if (out / "model.csv").exists():
        return
    model = sm.tsa.DynamicFactorMQ(new, factors=factors, factor_multiplicities=factor_multiplicities)
    try:
        results = model.fit(disp=10, maxiter=5_000)
    except Exception as e:
        with open(outdir / "failed.txt", "a") as f:
            f.write(f"{state}\t{e}\n")
        return
    with open(out / "model.csv", "w") as f:
        f.write(model.summary().as_csv())
    with open(out / "results.csv", "w") as f:
        f.write(results.summary().as_csv())
    filtered = results.factors["filtered"]
    filtered["State"] = state
    filtered.to_csv(out / "filtered-factors.csv")
    return model


@st.cache_data
def get_data():
    return get_df()


df = get_df()
sub = pd.Series([x for x in df.columns if x not in ["State", "Time"]], name="Variables").to_frame()
factors = get_factors()
factor_vars = list(factors.keys())
_ = [factors.pop(x) for x in factor_vars if x not in df.columns]
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
        selectors[group] = stcol.multiselect(group, variables, DEFAULTS[group])

    # State selections
    state_sel = st.multiselect("States", df.State.unique(), default=df.State.unique())
    c1, c2 = st.columns([0.7, 0.3])
    outdir = c1.text_input("Output Directory", value="./")
    mult_sel = c2.slider("Global Multiplier", 0, 4, 2)

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
for x in selectors:
    columns.extend(selectors[x])
selectors.update({"global_multiplier": mult_sel, "outdir": outdir})
outdir = Path(outdir)
outdir.mkdir(exist_ok=True)
with open(outdir / "log.txt", "w") as f:
    json.dump(selectors, f)

progress_text = "Running model on designated states..."
my_bar = c.progress(0, text=progress_text)

n = len(state_sel)

for i, state in enumerate(state_sel):
    run_parameterized_model(df, state, outdir, columns=columns, global_multiplier=mult_sel)
    my_bar.progress((i + 1) / n, text=progress_text)

my_bar.empty()
filt_paths = [
    subdir / "filtered-factors.csv" for subdir in outdir.iterdir() if (subdir / "filtered-factors.csv").exists()
]
dfs = [pd.read_csv(x) for x in filt_paths]
filt_df = pd.concat(dfs)
filt_df.to_csv(outdir / "filtered-factors.csv")
st.dataframe(filt_df)

end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)
pprint(f"Runtime: {int(hours):0>2}H:{int(minutes):0>2}M:{seconds:05.2f}S")

st.balloons()