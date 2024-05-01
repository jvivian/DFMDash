#RESULTS
print(sc.original_data.weight_df)
print(sc.original_data.comparison_df)
print(sc.original_data.pen)

# Visualize
sc.plot(
    ["original", "pointwise", "cumulative"],
    treated_label="California",
    synth_label="Synthetic California",
    treatment_label="Pandemic Response",
#PLOT OF Y AND Y^
#VECTOR OF Wj