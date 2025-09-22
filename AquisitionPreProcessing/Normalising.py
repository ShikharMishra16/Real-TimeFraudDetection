import pandas as pd
from sklearn.preprocessing import StandardScaler

# 📥 Load the feature-engineered data
df = pd.read_csv("feature_engineered_creditcard.csv")

# 🧠 Columns to scale
to_scale = ['Amount', 'Txns_In_Hour', 'Amt_vs_HourAvg']

# 🔄 Apply Standard Scaler
scaler = StandardScaler()
df[to_scale] = scaler.fit_transform(df[to_scale])

print("✅ Scaled columns:", to_scale)

# 💾 Save final preprocessed data
df.to_csv("final_preprocessed_creditcard.csv", index=False)
print("✅ Final preprocessed dataset saved as 'final_preprocessed_creditcard.csv'")
