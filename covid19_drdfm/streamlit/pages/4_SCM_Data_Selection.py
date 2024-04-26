import numpy as np
import pandas as pd
from SyntheticControlMethods import DiffSynth, Synth
import pandas as pd
import plotly.io as pio
import streamlit as st

st.set_page_config(layout="wide")
pio.templates.default = "plotly_dark"

def center_title(text):
    return st.markdown(f"<h1 style='text-align: center; color: grey;'>{text}</h1>", unsafe_allow_html=True)

center_title("Synthetic Control Model Runner")




# DATA SELECTION

#SELECT H5AD FILE (DEFAULTS TO FILE USED FOR LAST DFM RUN)

#SELECT VARIABLES FOR PREVIEW TABLE
#DROP DOWNS TO SELECT SERIES FROM H5AD FILE
#CAN ADD OR REMOVE DROP DOWNS
#ALSO BUTTON TO ADD EVERY SERIES
#CAN ADD STATES OR LEAVE SOME OUT
#BUTTON TO GENERATE PREVIEW TABLE

#SELECT VARIABLES FOR MODEL
#SELECT Y (OUTCOME VARIABLE)
#SELECT TREATMENT STATE
#SELECT K PREDICTORS
#SELECT TREATMENT PERIOD
#BUTTON TO RUN MODEL