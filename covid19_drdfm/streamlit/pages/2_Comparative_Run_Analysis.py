from pathlib import Path

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import plotly.io as pio
import plotly_express as px
import pymc as pm
import streamlit as st

from covid19_drdfm.results import parse_multiple_runs

st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"


def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)


center_title("Comparative Run Analysis")

# Parameter to runs
run_dir = Path(st.text_input("Path directory of runs", value="./covid19_drdfm/data/example-data"))
df = parse_multiple_runs(run_dir)


def create_plot(df):
    # Create Streamlit expander for user inputs
    with st.expander("Filter options"):
        states = st.multiselect("Select States", df["State"].unique(), default=df["State"].unique())
    metric = st.sidebar.selectbox("Select Metric", df.columns[:3])
    nbins = st.sidebar.slider("nbins", min_value=10, max_value=500, value=50)
    log_x = st.sidebar.checkbox("Log X-axis")

    # Filter DataFrame based on user inputs
    df_filtered = df[df["State"].isin(states)]

    # Create Plotly figure
    fig = px.histogram(
        df_filtered,
        x=metric,
        color="Run",
        marginal="box",
        nbins=nbins,
        hover_data=["State"],
        log_x=log_x,
        opacity=0.5,
        barmode="overlay",
    )

    # Display Plotly figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    return metric


def count_failed_states(run_dir: Path, run_name: str):
    """Count the number of failed states for a specific run"""
    failed_file_path = run_dir / run_name / "failed.txt"
    if not failed_file_path.exists():
        return 0
    with open(failed_file_path) as failed_file:
        return len(failed_file.readlines())


def get_summary(df, run_name):
    # Median metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Number of Failed States", count_failed_states(run_dir, run_name))
    col2.metric("Median Log Likelihood", df["Log Likelihood"].median())
    col3.metric("Median AIC", df["AIC"].median())
    col4.metric("Median EM Iterations", df["EM Iterations"].median())


def show_summary(df):
    run = st.selectbox("Select a run", df["Run"].unique())
    filtered_df = df[(df["Run"] == run)]
    return get_summary(filtered_df, run)


def run_normal(df, metric):
    # Declare runs as a parameter
    with st.form("ABtest"):
        runs = st.multiselect("Select two runs A/B test", df.Run.sort_values().unique())
        submit = st.form_submit_button("Run Comparison")

    # Validation conditions
    if not submit:
        st.stop()
    if len(runs) != 2:
        st.warning("Only two runs may be selected, try again")

    run1, run2 = runs
    st.subheader(f"A/B Testing: {metric}")

    # Define model and run
    with st.spinner():
        mu_m = df[metric].mean()
        mu_s = df[metric].std()
        # st.write(f"mean: {mu_m}, sd: {mu_s}")
        with pm.Model():
            mu_1 = pm.Normal("group1_mean", mu=mu_m, sigma=mu_s)
            mu_2 = pm.Normal("group2_mean", mu=mu_m, sigma=mu_s)

            sd_1 = pm.HalfNormal("S1", 1)
            sd_2 = pm.HalfNormal("S2", 1)

            nu_minus_1 = pm.Exponential("nu_minus_one", 1 / 29)
            nu = pm.Deterministic("nu", nu_minus_1 + 1)

            pm.StudentT(run1, nu=nu, mu=mu_1, lam=sd_1**2, observed=df[df.Run == run1][metric])
            pm.StudentT(run2, nu=nu, mu=mu_2, lam=sd_2**2, observed=df[df.Run == run2][metric])

            diff = pm.Deterministic("Difference of Means", mu_1 - mu_2)
            pm.Deterministic("Difference of Stds", sd_1 - sd_2)
            pm.Deterministic("Effect Size", diff / np.sqrt((sd_1**2 + sd_2**2) / 2))
            return pm.sample()


def _ab_blurb():
    with st.expander("Bayesian A/B Testing"):
        st.markdown(
            """
            Use [Kruschke's](https://psycnet.apa.org/doiLanding?doi=10.1037%2Fa0029146) implementation to A/B test data

            Standard T-tests make implicit assumptions about data normality that can be inaccurate, particularly given
            sensitivities to outliers. Kruschke's version replaces the normal distribution with the [Student-T Distribution](https://en.wikipedia.org/wiki/Student%27s_t-distribution)
            which is more robust to outliers. It has the same parameters as a Gaussian
            """
        )
        st.latex(
            r"""
            f(x|\mu,\lambda,\nu) = \frac{\Gamma(\frac{\nu + 1}{2})}{\Gamma(\frac{\nu}{2})} \left(\frac{\lambda}{\pi\nu}\right)^{\frac{1}{2}} \left[1+\frac{\lambda(x-\mu)^2}{\nu}\right]^{-\frac{\nu+1}{2}}
            """
        )
        st.write("Three parameters: mean, precision (inverse variance), and degrees-of-freedom")
        st.write("The likelihood functions of our model are then:")
        st.latex(r"y^{(Group1)}_i \sim T(\nu, \mu_1, \sigma_1)")
        st.latex(r"y^{(Group2)}_i \sim T(\nu, \mu_2, \sigma_2)")
        st.write("The mean of the distribution can be modeled as Gaussian")
        st.latex(r"\mu_k \sim \mathcal{N}(\bar{x}, s)")
        st.write("Standard deviation as a Half-Normal")
        st.latex(r"\mu_k \sim \mathcal{HN}(\sigma)")
        st.write("Degrees-of-freedom can be modeled by an Exponential")
        st.latex(r"\nu = \lambda e^{-\lambda x}")
        st.write("Although we alter the implementation slightly to ensure the value is greater than 1")


def plot_trace(idata):
    f, ax = plt.subplots(2, 2)
    az.plot_trace(idata, axes=ax, var_names=["Difference of Means", "Effect Size"])
    plt.tight_layout()
    st.pyplot(f, use_container_width=True)


def plot_posterior(idata):
    f, ax = plt.subplots()
    az.plot_posterior(idata, var_names=["Difference of Means", "Effect Size"], ref_val=0, ax=ax)
    plt.tight_layout()
    st.pyplot(f, use_container_width=True)


def plot_forest(idata):
    f, ax = plt.subplots()
    az.plot_forest(idata, var_names=["group1_mean", "group2_mean"], ax=ax)
    plt.tight_layout()
    st.pyplot(f, use_container_width=True)


# Data
with st.expander("Data"):
    st.dataframe(df)

# Plot metrics across runs
metric = create_plot(df)

# Metrics by run in column form
with st.expander("Summary"):
    show_summary(df)

# Bayesian A/B Testing
_ab_blurb()
idata = run_normal(df, metric)
with st.expander("TracePlot"):
    plot_trace(idata)
with st.expander("Posterior"):
    plot_posterior(idata)
with st.expander("ForestPlot"):
    plot_forest(idata)
