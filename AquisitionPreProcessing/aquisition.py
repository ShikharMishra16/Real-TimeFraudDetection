import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📥 Load the dataset
df = pd.read_csv("creditcard.csv")

# 🔍 Overview
print("Dataset Shape:", df.shape)
print("\nFirst 5 Rows:\n", df.head())
print("\nData Types:\n", df.dtypes)
print("\nMissing Values:\n", df.isnull().sum())
print("\nClass Distribution (0 = normal, 1 = fraud):\n", df['Class'].value_counts())

# 🧮 Summary statistics
print("\nStatistical Summary:\n", df.describe())

# 📊 Visualizations

# Class distribution (Imbalance check)
plt.figure(figsize=(6, 4))
sns.countplot(x='Class', data=df)
plt.title("Class Distribution (0 = Normal, 1 = Fraud)")
plt.show()

# Transaction Amount Distribution
plt.figure(figsize=(8, 5))
sns.histplot(df['Amount'], bins=50, kde=True)
plt.title("Distribution of Transaction Amount")
plt.xlabel("Amount")
plt.ylabel("Frequency")
plt.show()

# Optional: Add a derived column from time
df['Hour'] = df['Time'] // 3600  # Convert seconds to hourly bins
