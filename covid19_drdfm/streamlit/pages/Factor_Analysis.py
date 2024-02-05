import streamlit as st
import json
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd
import plotly.io as pio
import plotly_express as px
import statsmodels.api as sm
import streamlit as st
from rich import print as pprint
from sklearn.preprocessing import MinMaxScaler

from covid19_drdfm.constants import FACTORS
from covid19_drdfm.dfm import state_process
from covid19_drdfm.processing import get_df


st.set_page_config(layout="wide")
pio.templates.default = "plotly_white"

st.write("yo!")
