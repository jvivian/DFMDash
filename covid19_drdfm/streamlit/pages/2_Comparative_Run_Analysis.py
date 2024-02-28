from pathlib import Path

import plotly.io as pio
import plotly_express as px
import streamlit as st

from covid19_drdfm.results import parse_multiple_runs

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"

# Parameter to runs
path_to_results = Path(
    st.text_input("Path directory of runs", value="./covid19_drdfm/data/example-data/test-all-global-2")
)

df = parse_multiple_runs(path_to_results)


def create_plot(df):
    # Create Streamlit expander for user inputs
    with st.expander("Filter options"):
        states = st.multiselect("Select States", df["State"].unique(), default=df["State"].unique())
    run = st.sidebar.selectbox("Select Metric", df.columns[:4])
    nbins = st.sidebar.slider("nbins", min_value=10, max_value=500, value=50)
    log_x = st.sidebar.checkbox("Log X-axis")

    # Filter DataFrame based on user inputs
    df_filtered = df[df["State"].isin(states)]

    # Create Plotly figure
    fig = px.histogram(df_filtered, x=run, color="Run", marginal="box", nbins=nbins, hover_data=["State"], log_x=log_x)
    # fig = ff.create_distplot(df_filtered, group_labels=df.Run.unique())

    # Display Plotly figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# Use the function
create_plot(df)
