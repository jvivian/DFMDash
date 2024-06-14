from pathlib import Path

import anndata as ann
import pandas as pd
import plotly.io as pio
import plotly_express as px
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

from covid19_drdfm.constants import FACTORS_GROUPED
from covid19_drdfm.covid19 import get_df

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"

EX_PATH = Path("./covid19_drdfm/data/example-data/pandemic-only")


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


def normalize(df):
    metadata = df[["State", "Time"]]
    df = df.drop(columns=["State", "Time"])
    df = pd.DataFrame(MinMaxScaler().fit_transform(df), columns=df.columns)
    df.index = metadata.index
    df[["State", "Time"]] = metadata[["State", "Time"]]
    return df


center_title("Factor Analysis")

# Read in data
# raw = get_df()
# TEST_DIR = Path('covid19_drdfm/data/example-output/')

# Parameter for results
def get_factors(res_dir):
    factor_path = res_dir / "factors.csv"
    df = pd.read_csv(factor_path, index_col=0)
    df["Time"] = df.index
    df.index.name = "Time"
    cols_to_drop = [x for x in df.columns if "Time." in x]
    df = df.drop(columns=cols_to_drop)
    df.columns = [x.lstrip("Factor_") for x in df.columns]
    return df


res_dir = Path(st.text_input("Path to results", value=EX_PATH))
if not res_dir:
    st.warning("Please provide and hit <ENTER>")
    st.stop()
df = get_factors(res_dir)

filter_list = ["Unnamed", "Time", "State"]
state = st.sidebar.selectbox("State", sorted(df.State.unique()))

with st.expander("State Factors"):
    st.dataframe(df[df.State == state])


# Grab first state to fetch valid variables
state_df = pd.read_csv(res_dir / state / "df.csv")
cols = [x for x in df.columns if x in state_df.columns] + ["State"]
# st.write(cols)
# Get factors and columns
# factor_vars = [x for x in FACTORS_GROUPED[factor.split("_")[1]] if x in valid_cols]  # and '_' in x]
# columns = [*factor_vars, "State", "Time"]

# Make df from res_dir
dfs = []
for subdir in res_dir.iterdir():
    if not subdir.is_dir():
        continue
    path = subdir / "df.csv"
    if not path.exists():
        st.write(f"Skipping {path}, not found")
        continue
    sub = pd.read_csv(path, index_col=0)
    sub["State"] = subdir.stem
    dfs.append(sub)

new = pd.concat(dfs)

# Normalize original data for state / valid variables
ad = ann.read_h5ad(res_dir / "data.h5ad")
factor_map = ad.var["factor"].to_frame()
factor_set = factor_map["factor"].unique().to_list() + [x for x in df.columns if "Global" in x]
# st.dataframe(factor_map)
factor = st.sidebar.selectbox("Factor", factor_set)
# new = ad.to_df().reset_index()
# new["State"] = ad.obs["State"].to_list()
# new = normalize(new[new.State == state])

# Normalize factors and add to new dataframe
# if st.sidebar.checkbox("Invert Factor"):
# df[factor] = df[factor] * -1
# df = normalize(df[df.State == state]).reset_index(drop=True)

df = df[df["State"] == state]
df = df[[factor]].join(new, on="Time")

# st.dataframe(df.head())
# st.dataframe(new.head())

# Coerce time bullshit to get dates standardized
# df["Time"] = pd.to_datetime(df["Time"]).dt.date
# new["Time"] = pd.to_datetime(new["Time"]).dt.date
with st.expander("Graph Data"):
    factor_cols = factor_map[factor_map["factor"] == factor]
    if factor_cols.empty:
        factor_cols = new.columns
    else:
        factor_cols = factor_cols.index.to_list()
        factor_cols += [factor]
    factor_cols = [x for x in factor_cols if x in df.columns]
    st.write(factor_cols)
    st.dataframe(df[factor_cols])

df = df[factor_cols].reset_index()

# Melt into format for plotting
# melted_df = df.drop(columns="State").melt(id_vars=["Time"], value_name="value")
melted_df = df.melt(id_vars=["Time"], value_name="value")
melted_df["Label"] = [5 if x == factor else 1 for x in melted_df.variable]

# Plot
f = px.line(melted_df, x="Time", y="value", color="variable", hover_data="variable", line_dash="Label")
st.plotly_chart(f, use_container_width=True)

# Model Results
results_path = res_dir / state / "results.csv"
model_path = res_dir / state / "model.csv"

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
