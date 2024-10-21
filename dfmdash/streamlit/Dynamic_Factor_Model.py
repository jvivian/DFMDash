from pathlib import Path
from typing import Optional

import anndata as ann
import pandas as pd
import plotly.io as pio
import streamlit as st

from dfmdash.dfm import ModelRunner

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


class DataHandler:
    """
    Handles data loading and preprocessing for a Streamlit application.
    """

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.ad: Optional[ann.AnnData] = None
        self.batch_col: Optional[str] = None
        self.non_batch_cols: Optional[list[str]] = None

    def get_data(self) -> "DataHandler":
        self.file_uploader().get_factor_mappings().create_anndata().apply_transforms()
        return self

    def file_uploader(self) -> "DataHandler":
        """
        Uploads a file and reads it into a DataFrame. Supported file types are CSV, TSV, and XLSX.

        Returns:
            A pandas DataFrame loaded from the uploaded file.

        Raises:
            RuntimeError: If no file is uploaded.
        """
        file = st.file_uploader("Upload a data file (CSV, TSV, XLSX)", type=["csv", "tsv", "xlsx"])
        load_covid_example = st.sidebar.checkbox("Load Covid Example")
        if file is None and not load_covid_example:
            st.warning("Please provide input file or check box in sidebar to see Covid-19 Example")
            st.stop()
        if load_covid_example:
            self.df = pd.read_csv(Path(__file__).parent / "../data/processed/test_input_2state.csv", index_col=0)
        else:
            self.df = self.load_data(file)
        c1, _, c2 = st.columns([0.25, 0.05, 0.7])
        with c2.expander("Raw Input Data"):
            st.dataframe(self.df)
        if self.df is None:
            st.error("DataFrame is empty! Check input data")
            st.stop()
        self.batch_col = c1.selectbox("Select a batch column (optional):", ["None", *list(self.df.columns)])
        if self.batch_col == "None":
            self.df["Batch"] = "Batch1"
            # self.batch_col = None
        self.non_batch_cols = [col for col in self.df.columns if col != self.batch_col]
        return self

    @staticmethod
    def load_data(file) -> pd.DataFrame:
        """
        Loads a DataFrame from an uploaded file based on its MIME type.

        Args:
            file: UploadedFile object from Streamlit.

        Returns:
            A DataFrame containing the data from the file.

        Raises:
            ValueError: If the file type is unsupported.
        """
        file_type = file.type.split("/")[-1]
        read_function = {
            "csv": lambda f: pd.read_csv(f, index_col=0),
            "tsv": lambda f: pd.read_csv(f, index_col=0, sep="\t"),
            "xlsx": lambda f: pd.read_excel(f, index_col=0),
        }.get(file_type, lambda _: None)

        if read_function is None:
            raise ValueError(f"Unsupported file type: {file_type}")

        return read_function(file)

    def apply_transforms(self) -> "DataHandler":
        st.subheader("Variable Transforms")
        options = st.multiselect("Select columns to apply transformations (optional):", self.non_batch_cols)
        transforms = {}
        for i, opt in enumerate(options):
            if i % 2 == 0:
                cols = st.columns(2)
            transform = cols[i % 2].radio(
                f"Select transform type for {opt}:", ("difference", "logdiff"), key=f"trans_{opt}"
            )
            transforms[opt] = transform
            if transform not in self.ad.var:
                self.ad.var[transform] = None
            self.ad.var.loc[opt, transform] = True
        return self

    def get_factor_mappings(self) -> "DataHandler":
        st.subheader("Map Factors to Variables")
        factor_input = st.text_input("Enter all factor options separated by space:")
        factor_options = factor_input.split()
        if not factor_options:
            st.warning("Enter at least one factor to assign to variables")
            st.stop()
        factor_mappings = {}
        for i, col in enumerate(self.non_batch_cols):
            if i % 2 == 0:
                cols = st.columns(2)
            col_factor = cols[i % 2].radio(
                f"Select factor for {col}:",
                options=factor_options,
                key=col,
                format_func=lambda x: f"{x}",
                horizontal=True,
            )
            if col_factor:
                factor_mappings[col] = col_factor

        if len(factor_mappings) != len(self.non_batch_cols):
            st.warning("Select a factor for each variable!")
            st.stop()
        self.factor_mappings = factor_mappings
        return self

    def create_anndata(self) -> "DataHandler":
        """
        Creates an AnnData object from the loaded DataFrame with optional batch column handling.

        Args:
            factor_mappings: A dictionary mapping column names to their respective factors.
            batch_col: Optional; the name of the column to use as the batch category.

        Returns:
            An AnnData object with additional metadata.
        """
        if self.batch_col and self.batch_col in self.df.columns:
            ad = ann.AnnData(self.df.drop(columns=[self.batch_col]))
            ad.obs[self.batch_col] = self.df[self.batch_col]
        else:
            ad = ann.AnnData(self.df)
        ad.var["factor"] = [self.factor_mappings[x] for x in self.non_batch_cols]
        self.ad = ad
        return self


def additional_params():
    with st.form("params"):
        c1, c2 = st.columns(2)
        global_multiplier = c1.slider("Global Multiplier", min_value=0, max_value=15, value=1)
        out_dir = c2.text_input("Output Directory", value="./DFM-results/")
        button = st.form_submit_button(label="Run Model")

    if not button:
        st.stop()

    return global_multiplier, Path(out_dir)


def run_model(ad, out_dir, batch, global_multiplier) -> ModelRunner:
    dfm = ModelRunner(ad, Path(out_dir), batch=batch)
    dfm.run(global_multiplier=global_multiplier)
    st.subheader("Results")
    for result in dfm.results:
        if batch is not None:
            st.subheader(result.name)
        st.write(result.result.summary())
        st.divider()
        st.write(result.model.summary())
    return dfm


center_title("Dynamic Factor Model Runner")
data = DataHandler().get_data()
ad = data.ad
global_multiplier, out_dir = additional_params()
batch = None if ad.obs.empty else ad.obs.columns[0]

with st.spinner("Running Model(s)..."):
    dfm = run_model(ad, out_dir, batch, global_multiplier)
    dfm.write_failures()
st.balloons()

filt_paths = [subdir / "factors.csv" for subdir in out_dir.iterdir() if (subdir / "factors.csv").exists()]
dfs = [pd.read_csv(x) for x in filt_paths]
try:
    filt_df = pd.concat([x for x in dfs if ~x.empty]).set_index("Time")
    filt_df.to_csv(out_dir / "factors.csv")
    st.dataframe(filt_df)
    #! TODO: Decide if i care enough
    # dfm.ad.write(out_dir / "data.h5ad")
    st.balloons()
except ValueError:
    st.error(f"No runs succeeded!! Check failures.txt in {out_dir}")
