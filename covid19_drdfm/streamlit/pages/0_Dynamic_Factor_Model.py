import time
from pathlib import Path

import pandas as pd
import plotly.io as pio
import streamlit as st
import yaml

from covid19_drdfm.constants import FACTORS
from covid19_drdfm.dfm import ModelRunner
import anndata as ann

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


def load_data(file):
    if "csv" in file.type:
        return pd.read_csv(file, index_col=0)
    elif "tsv" in file.type:
        return pd.read_csv(file, index_col=0, sep="\t")
    elif "xlsx" in file.type:
        return pd.read_excel(file, index_col=0)
    else:
        return None


def create_anndata(df, factor_mappings, batch_col=None):
    if batch_col:
        adata = ann.AnnData(df.drop(columns=batch_col))
        adata.obs[batch_col] = df[batch_col]
    else:
        adata = ann.AnnData(df)
    adata.var["factor"] = [factor_mappings[x] for x in adata.var.index]
    return adata


def file_uploader():
    # File uploader
    file = st.file_uploader("Upload a data file (CSV, TSV, XLSX)", type=["csv", "tsv", "xlsx"])
    if file is None:
        st.error("Please provide input file")
        st.stop()
    df = load_data(file)
    with st.expander("Raw Input Data"):
        st.dataframe(df)
    if df is not None:
        # Optional batch column
        batch_col = st.selectbox("Select a batch column (optional):", ["None"] + list(df.columns))
        if batch_col == "None":
            batch_col = None

        # Ask for non-batch variables and their factor mappings
        non_batch_cols = [col for col in df.columns if col != batch_col]
        factor_mappings = {}
        for col in non_batch_cols:
            factor = st.text_input(f"Enter factor for {col}:", key=col)
            if factor:
                # factor_cats = factor.split(",")
                # factor_mappings[col] = pd.Categorical(df[col], categories=factor_cats, ordered=True)
                factor_mappings[col] = factor
        if len(factor_mappings) != len(non_batch_cols):
            st.warning("Fill in a Factor label for all variables!")
            st.stop()

        # Create anndata
        ad = create_anndata(df, factor_mappings, batch_col)

        # Transformations
        options = st.multiselect(
            "Select columns to apply transformations:", non_batch_cols, format_func=lambda x: f"Transform {x}"
        )
        transforms = {}
        for opt in options:
            transform = st.radio(f"Select transform type for {opt}:", ("difference", "logdiff"), key=f"trans_{opt}")
            transforms[opt] = transform
            ad.var[transform] = None
            ad.var.loc[opt, transform] = True

        # Show anndata and transforms
        st.write("Anndata object:", ad)
        st.dataframe(ad.var)
    return ad


ad = file_uploader()

global_multiplier = st.slider("Global Multiplier", min_value=0, max_value=4, value=0)
outdir = st.text_input("Location of output!", value=None)
if not outdir:
    st.stop()
batch = None if ad.obs.empty else ad.obs.columns[0]
dfm = ModelRunner(ad, Path(outdir), batch=batch)
dfm.run(global_multiplier=global_multiplier)
st.write(dfm.results)
