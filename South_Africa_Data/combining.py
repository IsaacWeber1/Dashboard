import pandas as pd
import glob

files = glob.glob("*.csv")

combined_df = pd.DataFrame()

for file in files:
    df = pd.read_csv(file)
    combined_df = pd.concat([combined_df, df], ignore_index=True)

combined_df = combined_df.dropna(subset = ["Hydrogen Capabilities"])
combined_df = combined_df[combined_df["Hydrogen Capabilities"].str.strip() != ""]

combined_df.to_csv("combined_data.csv", index=False)
