import json

import pandas as pd
import plotly.io as pio
import plotly_express as px
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
import plotly.figure_factory as ff

from covid19_drdfm.processing import get_df, get_factors

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"

BAD_COLS = ["State", "Time"]


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


# def get_factors():
#     with open("covid19_drdfm/streamlit/factors.json") as f:
#         return json.load(f)


@st.cache_data
def get_data():
    return get_df()


df = get_data()
# df = df.drop(columns=["Proportion", "proportion_vax2"])

st.header("Input Data")
with st.expander("Factors"):
    st.write(get_factors())

with st.expander("Raw DataFrame"):
    st.dataframe(df)

with st.expander("MinMax Normalized Data"):
    sub = df.drop(columns=BAD_COLS)
    norm = pd.DataFrame(MinMaxScaler().fit_transform(sub), index=sub.index, columns=sub.columns)
    norm["State"] = df.State
    norm["Time"] = df.Time
    st.dataframe(norm)

with st.expander("Melt"):
    factors = get_factors()
    melt = norm.melt(id_vars=["State", "Time"])
    # melt["Group"] = [x.split("_")[0] for x in melt["variable"]]
    melt["Group"] = [factors[x][1] for x in melt.variable]
    st.dataframe(melt)

st.header("Plots")
with st.expander("Normalized Data by Time"):
    state_selector = st.sidebar.selectbox("State", df.State.unique())
    melt = melt[melt.State == state_selector]

    fig = px.line(
        melt,
        x="Time",
        y="value",
        color="Group",
        hover_data=["variable"],
        facet_col="Group",
        facet_col_wrap=2,
        log_y=True,
        height=666,
    )
    fig.update_yaxes(matches=None)
    fig.for_each_yaxis(lambda y: y.update(showticklabels=True))
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Correlation"):
    corr = norm.drop("State", axis=1).corr()
    fig = px.imshow(corr, height=1_000, color_continuous_scale="reds", color_continuous_midpoint=0.75, zmin=0, zmax=1)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Corr DataFrame"):
    st.dataframe(corr)

with st.expander("Dendrogram"):
    ddf = norm.drop(columns=["State", "Time"])
    for col in ddf.columns:
        ddf[col] = ddf[col].astype(float)
    fig = ff.create_dendrogram(ddf.T, labels=ddf.columns)
    fig.update_layout(width=800, height=500)
    st.plotly_chart(fig)


### AUTISM TEST AREA


def autism():
    data = {
        "John": {
            "Autism": 0.8,
            "Height": 0.1,
        },
        "Aaron": {
            "Autism": 0.95,
            "Height": 0.2,
        },
        "Nate": {"Autism": 0.5, "Height": 0.3},
        "Rob": {
            "Autism": 0.85,
            "Height": 0.9,
        },
        "Reese": {
            "Autism": 0.3,
            "Height": -0.5,
        },
        "Victor": {
            "Autism": -0.5,
            "Height": -0.3,
        },
        "Dillon": {
            "Autism": 0.25,
            "Height": 0.9,
        },
        "Steve": {"Autism": 0, "Height": 0},
        "Upgrayedd": {"Autism": -0.75, "Height": 0.35},
    }

    data = pd.DataFrame(data).T
    data["Name"] = data.index

    # st.dataframe(data)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.title("Test Area")

    center_title("FISTO Stats")
    c1, c2 = st.columns(2)
    x_sel = c1.selectbox("X", data.columns)
    y_sel = c2.selectbox("Y", [x for x in data.columns if x != x_sel])
    fig = px.scatter(data, x="Autism", y="Height", color="Name", height=600)
    fig.update_layout(yaxis_range=[-1, 1])
    fig.update_layout(xaxis_range=[-1, 1])
    fig.add_hline(y=0, line_color="grey", opacity=0.2)
    fig.add_vline(x=0, line_color="grey", opacity=0.2)
    fig.update_traces(marker=dict(size=12, line=dict(width=2, color="DarkSlateGrey")), selector=dict(mode="markers"))
    fig.update_yaxes(showticklabels=False)
    fig.update_xaxes(showticklabels=False)
    with st.expander("Plots"):
        st.plotly_chart(fig, use_container_width=True)
