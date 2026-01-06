# Financial Modeling Template in Python

import pandas as pd
import numpy as np

# Step 1: Input Historical Financial Data (Example Data)
# Usually, you would read this from Excel/CSV
data = {
    "Year": [2023, 2024, 2025],
    "Revenue": [1000, 1200, 1400],  # in millions
    "COGS": [400, 480, 560],
    "Operating_Expenses": [200, 240, 280],
    "Depreciation": [50, 60, 70],
    "Interest": [20, 25, 30],
    "Taxes": [80, 100, 120],
    "Capital_Expenditure": [100, 120, 140],
    "Change_in_Working_Capital": [20, 25, 30]
}

df = pd.DataFrame(data)

# Step 2: Calculate EBIT, EBT, and Net Income
df["EBIT"] = df["Revenue"] - df["COGS"] - df["Operating_Expenses"] - df["Depreciation"]
df["EBT"] = df["EBIT"] - df["Interest"]
df["Net_Income"] = df["EBT"] - df["Taxes"]

# Step 3: Calculate Free Cash Flow (FCF)
df["FCF"] = df["Net_Income"] + df["Depreciation"] - df["Capital_Expenditure"] - df["Change_in_Working_Capital"]

# Step 4: Forecast Future Years using growth rate
growth_rate = 0.1  # 10% growth for Revenue
forecast_years = 3
last_year = df.iloc[-1]

for i in range(1, forecast_years+1):
    next_year = {}
    next_year["Year"] = last_year["Year"] + 1
    next_year["Revenue"] = last_year["Revenue"] * (1 + growth_rate)
    next_year["COGS"] = last_year["COGS"] * (1 + growth_rate)
    next_year["Operating_Expenses"] = last_year["Operating_Expenses"] * (1 + growth_rate)
    next_year["Depreciation"] = last_year["Depreciation"] * (1 + growth_rate)
    next_year["Interest"] = last_year["Interest"] * (1 + growth_rate)
    next_year["Taxes"] = last_year["Taxes"] * (1 + growth_rate)
    next_year["Capital_Expenditure"] = last_year["Capital_Expenditure"] * (1 + growth_rate)
    next_year["Change_in_Working_Capital"] = last_year["Change_in_Working_Capital"] * (1 + growth_rate)
    
    next_year["EBIT"] = next_year["Revenue"] - next_year["COGS"] - next_year["Operating_Expenses"] - next_year["Depreciation"]
    next_year["EBT"] = next_year["EBIT"] - next_year["Interest"]
    next_year["Net_Income"] = next_year["EBT"] - next_year["Taxes"]
    next_year["FCF"] = next_year["Net_Income"] + next_year["Depreciation"] - next_year["Capital_Expenditure"] - next_year["Change_in_Working_Capital"]
    
    df = pd.concat([df, pd.DataFrame([next_year])], ignore_index=True)
    last_year = next_year

# Step 5: Discounted Cash Flow (DCF) Valuation
discount_rate = 0.12  # 12% cost of capital
df["Discount_Factor"] = [(1/(1+discount_rate))**i for i in range(1, len(df)+1)]
df["DCF"] = df["FCF"] * df["Discount_Factor"]

npv = df["DCF"].sum()

# Step 6: Output Results
print("\n===== Financial Model =====")
print(df[["Year","Revenue","EBIT","Net_Income","FCF","DCF"]])
print(f"\nNet Present Value (NPV) of Future Cash Flows: {npv:.2f} million")
