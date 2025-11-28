import pandas as pd

df = pd.read_csv("cleaned_creditcard.csv")
print("Initial shape:", df.shape)

# Convert 'Time' (in seconds) into Hour blocks
df['Hour'] = df['Time'] // 3600

# Add Night-time Transaction Flag
df['Is_Night'] = df['Hour'].apply(lambda x: 1 if (x < 6 or x > 22) else 0)

# Bin the 'Amount' column into 4 quantile-based groups
df['Amount_Bin'] = pd.qcut(df['Amount'], q=4, labels=['low', 'medium', 'high', 'very_high'])

# Count transactions per hour block
txn_per_hour = df.groupby('Hour').size()
df['Txns_In_Hour'] = df['Hour'].map(txn_per_hour)

# Calculate mean amount per hour
avg_amt_per_hour = df.groupby('Hour')['Amount'].mean()
df['Amt_vs_HourAvg'] = df.apply(lambda row: row['Amount'] / avg_amt_per_hour[row['Hour']] if avg_amt_per_hour[row['Hour']] != 0 else 0, axis=1)

df = pd.get_dummies(df, columns=['Amount_Bin'], drop_first=True)

df.to_csv("feature_engineered_creditcard.csv", index=False)
print("✅ Feature engineered dataset saved as 'feature_engineered_creditcard.csv'")
print("✅ Final shape after feature engineering:", df.shape)
