import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set(style='whitegrid')
os.makedirs("plots", exist_ok=True)

# -------------------------------
# 1. Plot Fraud Class Metrics
# -------------------------------
df_class = pd.read_csv("supervised_classification_report.csv")

# Check if required columns exist
if 'Model' not in df_class.columns or 'index' not in df_class.columns:
    raise ValueError("CSV missing 'Model' or 'index' column")

# Filter for fraud class (label '1')
df_fraud = df_class[df_class['index'].astype(str) == '1'].copy()

# Ensure correct melt
if not df_fraud.empty:
    df_fraud_melted = df_fraud.melt(
        id_vars=['Model'],
        value_vars=['precision', 'recall', 'f1-score'],
        var_name='Metric',
        value_name='Score'
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_fraud_melted, x='Model', y='Score', hue='Metric', palette='Set2')
    plt.title("Precision, Recall, F1-Score (Fraud Class Only)")
    plt.ylim(0, 1)
    plt.ylabel("Score")
    plt.xlabel("Model")
    plt.legend(title="Metric", bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("plots/fraud_class_metrics.png", bbox_inches='tight')
    plt.show()
else:
    print("⚠️ No fraud class data found in classification report!")

# -------------------------------
# 2. Plot AUC/LogLoss Comparison
# -------------------------------
df_auc = pd.read_csv("supervised_auc_logloss_report.csv")

# Drop NaNs and validate structure
df_auc = df_auc.dropna()
if not all(col in df_auc.columns for col in ['Model', 'Metric', 'Score']):
    raise ValueError("supervised_auc_logloss_report.csv must contain 'Model', 'Metric', and 'Score' columns")

plt.figure(figsize=(12, 6))
sns.barplot(data=df_auc, x='Model', y='Score', hue='Metric', palette='Set1')
plt.title("ROC-AUC, PR-AUC, and Log Loss Comparison")
plt.ylabel("Score")
plt.xlabel("Model")
plt.legend(title="Metric", bbox_to_anchor=(1.02, 1), loc='upper left')

# Add score labels
for bar in plt.gca().patches:
    height = bar.get_height()
    plt.gca().text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.01,
        f"{height:.3f}",
        ha='center',
        fontsize=9
    )

plt.tight_layout()
plt.savefig("plots/auc_logloss_comparison.png", bbox_inches='tight')
plt.show()