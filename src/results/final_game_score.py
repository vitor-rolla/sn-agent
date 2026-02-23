#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.patches as mpatches

data = {
    "Gemini-3.1-pro-preview": [81.63, 75.51, 67.35],
    "Gemini-3-flash-preview": [91.84, 93.88, 55.1],
    "Gemini-2.5-flash":       [63.27, 69.39, 63.27],
    "Gemini-2.5-flash-lite":  [40.82, 24.49, 10.2],
    "Gpt-4o":                 [71.43, 81.63, 48.98],
    "Gpt-4o-mini":            [42.86, 51.02, 20.41],
    "Gpt-5-nano":             [32.65, 24.49, 22.45]
}
#"gpt-5-nano": [,,],

index = [
"Default",
"Literal",
"Complex"
]

df = pd.DataFrame(data, index=index)
df_long = df.reset_index().melt(
    id_vars="index",
    var_name="technique",
    value_name="score"
)

# -------------------------
# Plot configuration
# -------------------------
colors = [
    "#95f9c3", "#7ed9b4", "#67b9a4",
    "#509995", "#397885", "#225876", "#0b3866"
]

custom_hatches = ["//", "\\\\", "xxx", "-----", "//////", "xx", "\\\\\\\\\\\\\\\\"]

sns.set(style="whitegrid")
plt.rcParams["font.family"] = "DejaVu Serif"

fig = plt.figure(figsize=(20, 8))

bar_plot = sns.barplot(
    x="index",
    y="score",
    hue="technique",
    data=df_long,
    orient="v",
    palette=colors
)

# -------------------------
# Apply hatches per model
# -------------------------
bars_per_group = len(index)

for i, bar in enumerate(bar_plot.patches):
    hatch_idx = i // bars_per_group
    bar.set_hatch(custom_hatches[hatch_idx])

# -------------------------
# Annotate bars with values
# -------------------------
for container in bar_plot.containers:
    for rect in container:
        height = rect.get_height()
        bar_plot.annotate(
            f"{height:.1f}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
            size=9,
        )

# -------------------------
# Labels and formatting
# -------------------------
plt.xlabel("prompt type", size=20, labelpad=10)
plt.ylabel("score (%)", size=20)

plt.tick_params(axis='y', labelsize=14)
plt.tick_params(axis='x', labelsize=14)

# Custom legend with correct hatching
legend_handles = [
    mpatches.Patch(facecolor=color, edgecolor='white', hatch=hatch)
    for hatch, color in zip(custom_hatches, colors)
]

plt.legend(
    legend_handles,
    df_long["technique"].unique(),
    loc="upper center",
    ncol=7,
    bbox_to_anchor=(0.5, 1.1),
    prop={'size': 10}
)

plt.tight_layout()

# -------------------------
# Save and show
# -------------------------
fig.savefig("task_driven_normal.pdf", transparent=False)
plt.show()


