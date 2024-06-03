import anndata as ann
import numpy as np
import pandas as pd
from SyntheticControlMethods import DiffSynth, Synth
import pandas as pd
import plotly.io as pio
import streamlit as st
from covid19_drdfm.constants import FACTORS_GROUPED
from covid19_drdfm.covid19 import get_df, get_project_h5ad
from pathlib import Path

st.set_page_config(layout="wide")
pio.templates.default = "plotly_dark"

EX_PATH = Path("./covid19_drdfm/data/example-data/test-all-global-1_2019")


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


center_title("Synthetic Control Model Runner")

# DATA SELECTION
result_dir = Path(st.text_input("Result Directory", value=EX_PATH))
h5ad_path = result_dir / "data.h5ad"
factors_path = result_dir / "factors.csv"

ad = ann.read_h5ad(h5ad_path)
fdf = pd.read_csv(factors_path)
cols_to_drop = [x for x in fdf.columns if "Time." in x]
fdf = fdf.drop(columns=cols_to_drop)
fdf.columns = [x.lstrip("Factor_") for x in fdf.columns]
st.write(ad)
# st.dataframe(fdf)

dfs = []
for subdir in result_dir.iterdir():
    if not subdir.is_dir():
        continue
    state = pd.read_csv(subdir / "df.csv")
    state["State"] = subdir.stem
    dfs.append(state)
df = pd.concat(dfs)
fdf = fdf.set_index("Time")
columns = [x for x in fdf.columns if x not in df.columns] + ["State"]
fdf = fdf[columns]
st.dataframe(df)
st.dataframe(fdf)
st.stop()

# SELECT VARIABLES FOR PREVIEW TABLE
# DROP DOWNS TO SELECT SERIES FROM H5AD FILE
# CAN ADD OR REMOVE DROP DOWNS
# ALSO BUTTON TO ADD EVERY SERIES
# CAN ADD STATES OR LEAVE SOME OUT
# BUTTON TO GENERATE PREVIEW TABLE

# Multiselect for input columns

# SELECT VARIABLES FOR MODEL


# st.write(Synth)
# sc = Synth(df, factor, "State", "Time", treatment_month, state, n_optim=10, pen="auto")


# SELECT Y (OUTCOME VARIABLE)
# SELECT TREATMENT STATE
# SELECT K PREDICTORS
# SELECT TREATMENT PERIOD
# BUTTON TO RUN MODEL
