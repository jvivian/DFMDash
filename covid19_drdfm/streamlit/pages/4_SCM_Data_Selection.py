import anndata as ann
import numpy as np
import pandas as pd
from SyntheticControlMethods import DiffSynth, Synth
import pandas as pd
import plotly.io as pio
import streamlit as st
from covid19_drdfm.constants import FACTORS_GROUPED
from covid19_drdfm.covid19 import get_df, get_project_h5ad

st.set_page_config(layout="wide")
pio.templates.default = "plotly_dark"


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


center_title("Synthetic Control Model Runner")


# DATA SELECTION

# SELECT H5AD FILE (DEFAULTS TO FILE USED FOR LAST DFM RUN)
h5ad_path = st.text_input("H5AD path", value="./covid19_drdfm/data/processed/data.h5ad")
factor_path = st.text_input("Factor path from successful run", value="covid19_drdfm/data/example-data/test-all-global-1_2019/filtered-factors.csv")

ad = ann.read_h5ad(h5ad_path)
st.write(ad)
#st.dataframe(ad.uns["factors"])

# Read in data
ad = get_project_h5ad()
df = ad.to_df()
df["Time"] = df.index
df["State"] = ad.obs.State
st.dataframe(ad.obs)
st.dataframe(ad.var)
# Parameters
state = st.sidebar.selectbox("Select Treatment State", sorted(ad.obs["State"].unique()))
factor = st.sidebar.selectbox("Factor", sorted(FACTORS_GROUPED))
treatment_month = st.sidebar.selectbox("Select Treatment Time", ad.obs.index)
date_start = st.sidebar.selectbox("Start Date", value=df.Time.min(), min_value=df.Time.min(), max_value=ad.obs.Time.max())


fdf = pd.read_csv(factor_path) 
fdf = fdf.sort_values(["State", "Time"])
df = df[df.Time > "2019-02-01"] #update tp be first in fdf
df[factor] = fdf[factor].to_list()
st.write(df)




# SELECT VARIABLES FOR PREVIEW TABLE
# DROP DOWNS TO SELECT SERIES FROM H5AD FILE
# CAN ADD OR REMOVE DROP DOWNS
# ALSO BUTTON TO ADD EVERY SERIES
# CAN ADD STATES OR LEAVE SOME OUT
# BUTTON TO GENERATE PREVIEW TABLE
# SELECT VARIABLES FOR MODEL


st.write(Synth)
sc = Synth(df, factor, "State", "Time", treatment_month, state, n_optim=10, pen="auto")



# SELECT Y (OUTCOME VARIABLE)
# SELECT TREATMENT STATE
# SELECT K PREDICTORS
# SELECT TREATMENT PERIOD
# BUTTON TO RUN MODEL
