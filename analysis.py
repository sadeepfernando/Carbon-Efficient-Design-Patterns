import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

# ----------------------------
# 1️⃣ Load execution summary
# ----------------------------
exec_df = pd.read_csv("execution_summary.csv")

exec_df["avg_execution_time_s"] = exec_df["avg_execution_time_ms"] / 1000

# ----------------------------
# 2️⃣ Process HWInfo files
# ----------------------------

POWER_COLUMN = "CPU Package Power [W]"   # Adjust if needed
hwinfo_files = glob.glob("hwinfo_files/*.CSV")

power_results = []

for file in hwinfo_files:
    df = pd.read_csv(file, encoding="latin1")
    df.columns = df.columns.str.strip()

    if POWER_COLUMN not in df.columns:
        continue

    df = df.dropna(subset=[POWER_COLUMN])

    # Remove units and unwanted characters
    df[POWER_COLUMN] = (
        df[POWER_COLUMN]
        .astype(str)
        .str.replace(",", ".", regex=False)   # convert decimal comma
        .str.replace(" W", "", regex=False)   # remove unit if exists
        .str.strip()
    )

    # Convert to numeric safely
    df[POWER_COLUMN] = pd.to_numeric(df[POWER_COLUMN], errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=[POWER_COLUMN])

    avg_power = df[POWER_COLUMN].mean()

    # Extract pattern & language from filename
    filename = os.path.basename(file).replace(".CSV", "")
    pattern, language = filename.split("_")

    power_results.append({
        "pattern": pattern,
        "language": language,
        "avg_power_w": avg_power
    })

power_df = pd.DataFrame(power_results)

# ----------------------------
# 3️⃣ Merge Execution + Power
# ----------------------------
merged = pd.merge(exec_df, power_df, on=["pattern", "language"])

# ----------------------------
# 4️⃣ Compute Energy
# ----------------------------
merged["energy_j"] = merged["avg_execution_time_s"] * merged["avg_power_w"]

# ----------------------------
# 5️⃣ Carbon Emission
# ----------------------------
emission_factor = 0.6  # Sri Lanka kgCO2/kWh

merged["energy_kwh"] = merged["energy_j"] / 3600000
merged["carbon_kg"] = merged["energy_kwh"] * emission_factor

# ----------------------------
# 6️⃣ Energy per message
# ----------------------------
merged["energy_per_message_j"] = merged["energy_j"] / merged["runs"]


# ----------------------------
# 9️⃣ Percentage Difference (Python vs Java)
# ----------------------------

merged["energy_diff_vs_java_%"] = None

for pattern in merged["pattern"].unique():
    subset = merged[merged["pattern"] == pattern]

    if "java" in subset["language"].values and "python" in subset["language"].values:
        java_energy = subset[subset["language"]=="java"]["energy_j"].values[0]
        python_energy = subset[subset["language"]=="python"]["energy_j"].values[0]

        diff = ((python_energy - java_energy) / java_energy) * 100

        merged.loc[
            (merged["pattern"]==pattern) & (merged["language"]=="python"),
            "energy_diff_vs_java_%"
        ] = round(diff,2)

print("\nPercentage Difference (Python vs Java):")
print(merged[["pattern","language","energy_diff_vs_java_%"]])

# ----------------------------
# 1️⃣1️⃣ Correlation Analysis
# ----------------------------

correlation = merged["energy_j"].corr(merged["avg_execution_time_ms"])

print("\nCorrelation between Execution Time and Energy:", round(correlation,3))

# ----------------------------
# 1️⃣2️⃣ Independent t-test
# ----------------------------

# from scipy.stats import ttest_ind

# java_energy = merged[merged["language"]=="java"]["energy_j"]
# python_energy = merged[merged["language"]=="python"]["energy_j"]

# t_stat, p_value = ttest_ind(java_energy, python_energy)

# print("\nT-test Results:")
# print("T-statistic:", round(t_stat,3))
# print("P-value:", round(p_value,5))

# if p_value < 0.05:
#     print("Result: Statistically Significant Difference")
# else:
#     print("Result: No Statistically Significant Difference")

# ----------------------------
# 7️⃣ Save Final Results
# ----------------------------
merged.to_csv("final_research_results.csv", index=False)

print("Final Results:")
print(merged)

# ----------------------------
# 8️⃣ Visualization
# ----------------------------


color_java = "#2E8B57"   # Green
color_python = "#FF8C00" # Orange
width = 0.35

patterns = merged["pattern"].unique()
x = range(len(patterns))

plt.figure(figsize=(8,5))

java_vals = merged[merged["language"]=="java"].set_index("pattern").loc[patterns]["energy_j"]
python_vals = merged[merged["language"]=="python"].set_index("pattern").loc[patterns]["energy_j"]

plt.bar([i - width/2 for i in x], java_vals, width=width, label="Java", color=color_java)
plt.bar([i + width/2 for i in x], python_vals, width=width, label="Python", color=color_python)

plt.xticks(x, patterns)
plt.ylabel("Energy (J)")
plt.title("Energy Consumption by Pattern and Language")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.6)

plt.savefig("energy_comparison.png")
plt.close()

plt.figure(figsize=(8,5))

java_vals = merged[merged["language"]=="java"].set_index("pattern").loc[patterns]["avg_execution_time_ms"]
python_vals = merged[merged["language"]=="python"].set_index("pattern").loc[patterns]["avg_execution_time_ms"]

plt.bar([i - width/2 for i in x], java_vals, width=width, label="Java", color=color_java)
plt.bar([i + width/2 for i in x], python_vals, width=width, label="Python", color=color_python)

plt.xticks(x, patterns)
plt.ylabel("Execution Time (ms)")
plt.title("Execution Time by Pattern and Language")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.6)

plt.savefig("time_comparison.png")
plt.close()

plt.figure(figsize=(8,5))

java_vals = merged[merged["language"]=="java"].set_index("pattern").loc[patterns]["avg_power_w"]
python_vals = merged[merged["language"]=="python"].set_index("pattern").loc[patterns]["avg_power_w"]

plt.bar([i - width/2 for i in x], java_vals, width=width, label="Java", color=color_java)
plt.bar([i + width/2 for i in x], python_vals, width=width, label="Python", color=color_python)

plt.xticks(x, patterns)
plt.ylabel("Average Power (W)")
plt.title("Average CPU Power by Pattern and Language")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.6)

plt.savefig("power_comparison.png")
plt.close()

overall = merged.groupby("language")[["energy_j"]].mean()

plt.figure(figsize=(6,5))
plt.bar(overall.index, overall["energy_j"], color=[color_java, color_python])

plt.ylabel("Average Energy (J)")
plt.title("Overall Average Energy by Language")
plt.grid(axis="y", linestyle="--", alpha=0.6)

plt.savefig("overall_energy.png")
plt.close()