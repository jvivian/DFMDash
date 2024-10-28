from pathlib import Path

import pandas as pd
import plotly.io as pio
import plotly_express as px
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"

FILE = Path(__file__)
EX_PATH = FILE.parent / "../../../data/example-data/pandemic-only"


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


def normalize(df, batch_col=None):
    time = df.index
    if batch_col:
        batch_column = df[batch_col].copy()
        df = df.drop(columns=[batch_col])
        df = pd.DataFrame(MinMaxScaler().fit_transform(df), columns=df.columns, index=time)
        df[batch_col] = batch_column
    else:
        df = pd.DataFrame(MinMaxScaler().fit_transform(df), columns=df.columns, index=time)
    return df


center_title("Factor Analysis")


# Parameter for results
def get_factors(res_dir):
    try:
        factor_path = res_dir / "factors.csv"
        df = pd.read_csv(factor_path, index_col=0)
        df["Time"] = df.index
        df.index.name = "Time"
        cols_to_drop = [x for x in df.columns if "time" in x.lower()]
        df = df.drop(columns=cols_to_drop)
        df.columns = [x.lstrip("Factor_") for x in df.columns]
    except FileNotFoundError:
        st.error(
            f"The path provided does not contain results from the Dynamic Factor Model, please double check: {res_dir}"
        )
        st.stop()
    return df


def parse_factor_blocks(file_path: Path) -> list[str]:
    factor_blocks = []
    start_collecting = False

    with file_path.open("r") as file:
        for line in file:
            if "order" in line:
                start_collecting = True
                continue

            if start_collecting:
                if line.strip():
                    factor_name = line.split(",")[0].strip()
                    factor_blocks.append(factor_name)
                else:
                    break

    return factor_blocks


res_dir = Path(st.text_input("Path to results", value=EX_PATH))
if not res_dir:
    st.warning("Please provide and hit <ENTER>")
    st.stop()
df = get_factors(res_dir)

# ? Filter out values based on `df.csv`
batch_colname = None
subdir = None
if (res_dir / "df.csv").exists():
    batch_col = None
    input_df = pd.read_csv(res_dir / "df.csv", index_col=0)
    st.sidebar.subheader("Single Batch Found")
else:
    subdir = next(x for x in res_dir.iterdir() if x.is_dir())
    input_df = pd.read_csv(subdir / "df.csv", index_col=0)
    batch_colname = df.columns[-1]
    batch_col = st.sidebar.selectbox("Select Batch Variable", options=sorted(df[df.columns[-1]].unique()))


filter_list = ["Unnamed", "Time"]


df = df[df[batch_colname] == batch_col] if batch_col else df
with st.expander("Factors"):
    st.dataframe(df)

# Normalize original data for state / valid variables
if subdir:
    factor_set = parse_factor_blocks(subdir / "model.csv") + [x for x in df.columns if "Global" in x]
else:
    factor_set = parse_factor_blocks(res_dir / "model.csv") + [x for x in df.columns if "Global" in x]

factor = st.sidebar.selectbox("Factor", set(sorted(factor_set)))

# Normalize factors and add to new dataframe
if st.sidebar.checkbox("Invert Factor"):
    df[factor] = df[factor] * -1
df = normalize(df, batch_colname) if batch_col else normalize(df)


df = df[[factor]].join(input_df)

col_opts = [x for x in df.columns.to_list() if x != batch_col]
cols = st.multiselect("Variables to plot", col_opts, default=col_opts)
with st.expander("Graph Data"):
    st.dataframe(df[cols])

df = df[cols].reset_index()

# Melt into format for plotting
melted_df = df.melt(id_vars=["Time"], value_name="value")
melted_df["Label"] = [5 if x == factor else 1 for x in melted_df.variable]

# Plot
f = px.line(melted_df, x="Time", y="value", color="variable", hover_data="variable", line_dash="Label")
st.plotly_chart(f, use_container_width=True)

# Model Results
if batch_col:
    results_path = res_dir / batch_col / "results.csv"
    model_path = res_dir / batch_col / "model.csv"
else:
    results_path = res_dir / "results.cvs"
    model_path = res_dir / "model.csv"

# Metrics for run
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

# TODO: The first column _must_ be set to `Time` by the Dynamic Factor Model page!
