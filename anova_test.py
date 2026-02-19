import os
import sqlite3
import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import statsmodels.api as sm

# ==============================
# CONFIGURATION
# ==============================

DB_PATH = "telemetry_results.db"
HWINFO_FOLDER = "hwinfo_files"
POWER_COLUMN = "CPU Package Power [W]"   # CHANGE if needed

# ==============================
# 1. LOAD EXECUTION TIME DATA
# ==============================

def load_execution_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT pattern, language, execution_time_ms
        FROM benchmark_results
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["execution_time_s"] = df["execution_time_ms"] / 1000.0
    return df


# ==============================
# 2. EXTRACT AVERAGE POWER
# ==============================

def extract_average_power():
    power_data = []

    for file in os.listdir(HWINFO_FOLDER):
        if file.lower().endswith(".csv"):

            file_path = os.path.join(HWINFO_FOLDER, file)

            try:
                df = pd.read_csv(file_path, encoding="latin1")

                if POWER_COLUMN not in df.columns:
                    print(f"⚠ Power column not found in {file}")
                    continue

                # FORCE NUMERIC CONVERSION
                df[POWER_COLUMN] = pd.to_numeric(
                    df[POWER_COLUMN],
                    errors="coerce"
                )

                # DROP invalid values
                df_clean = df.dropna(subset=[POWER_COLUMN])

                if df_clean.empty:
                    print(f"⚠ No valid power data in {file}")
                    continue

                avg_power = df_clean[POWER_COLUMN].mean()

                # Extract pattern and language
                # Example: decorator_java.CSV
                name = file.replace(".csv", "").replace(".CSV", "")
                parts = name.split("_")

                if len(parts) != 2:
                    print(f"⚠ Filename format incorrect: {file}")
                    continue

                pattern = parts[0]
                language = parts[1]

                power_data.append({
                    "pattern": pattern,
                    "language": language,
                    "average_power_w": avg_power
                })

                print(f"✓ Processed {file} | Avg Power = {avg_power:.2f} W")

            except Exception as e:
                print(f"Error reading {file}: {e}")

    if not power_data:
        print("❌ No power data extracted!")
        return pd.DataFrame(columns=["pattern", "language", "average_power_w"])

    return pd.DataFrame(power_data)


# ==============================
# 3. MERGE DATA & COMPUTE ENERGY
# ==============================

def prepare_final_dataset(exec_df, power_df):
    merged = pd.merge(exec_df, power_df,
                      on=["pattern", "language"],
                      how="inner")

    merged["energy_j"] = (
        merged["execution_time_s"] *
        merged["average_power_w"]
    )

    return merged


# ==============================
# 4. TWO-WAY ANOVA
# ==============================

def run_two_way_anova(df):

    print("\n==============================")
    print(" TWO-WAY ANOVA: Energy")
    print(" Factors: Pattern × Language")
    print("==============================\n")

    model = ols(
        'energy_j ~ C(pattern) + C(language) + C(pattern):C(language)',
        data=df
    ).fit()

    anova_table = sm.stats.anova_lm(model, typ=2)
    print(anova_table)

    print("\nModel Summary:")
    print(model.summary())


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    print("Loading execution time data...")
    exec_df = load_execution_data()

    print("Extracting power data from HWINFO logs...")
    power_df = extract_average_power()

    print("Merging datasets and computing energy...")
    final_df = prepare_final_dataset(exec_df, power_df)

    print("\nFinal Dataset Preview:")
    print(final_df.head())

    run_two_way_anova(final_df)