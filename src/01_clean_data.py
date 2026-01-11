import os
import pandas as pd

# path to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# project root
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# paths
RAW_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "transactions.xlsx")
PROCESSED_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "transactions_clean.csv")

# read raw Excel data (skip first 9 rows for header)
df = pd.read_excel(RAW_FILE, header=9)

# clean column names (keep only text after last comma)
df.columns = [col.split(",")[-1].strip() for col in df.columns]

# drop first 8 rows and rename date column
df = df.iloc[8:].reset_index(drop=True)
df.rename(columns={"Título": "Date"}, inplace=True)

# convert all columns except 'Date' to numeric
for col in df.columns:
    if col != 'Date':
        df[col] = pd.to_numeric(df[col], errors='coerce')

# reorder columns: put 'acapulco' first
cols = ['Acapulco de Juárez'] + [c for c in df.columns if c != 'Acapulco de Juárez']
df = df[cols]

# Optional: check result
print(df.head())

# save cleaned data to processed folder
os.makedirs(os.path.join(PROJECT_ROOT, "data", "processed"), exist_ok=True)
df.to_csv(PROCESSED_FILE, index=False)
print("Cleaned data saved to", PROCESSED_FILE)
