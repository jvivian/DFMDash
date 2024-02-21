from os import rename

import numpy as np
import pandas as pd
from SyntheticControlMethods import DiffSynth, Synth

# Import data
data_dir = "https://raw.githubusercontent.com/OscarEngelbrektson/SyntheticControlMethods/master/examples/datasets/"
df = pd.read_csv(data_dir + "smoking_data" + ".csv")


# Fit Differenced Synthetic Control
df = df.rename(columns={"cigsale": "Pandemic"})
sc = Synth(df, "Pandemic", "state", "year", 1989, "California", n_optim=10, pen="auto")

print(sc.original_data.weight_df)
print(sc.original_data.comparison_df)
print(sc.original_data.pen)

# Visualize
sc.plot(
    ["original", "pointwise", "cumulative"],
    treated_label="California",
    synth_label="Synthetic California",
    treatment_label="Pandemic Response",
)
