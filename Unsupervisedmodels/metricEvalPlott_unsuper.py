import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set(style="whitegrid")
os.makedirs("plots", exist_ok=True)

# Load evaluation CSV
df = pd.read_csv("unsupervised_evaluation.csv")

# -----------------------------
# Plot: Precision, Recall, F1
# -----------------------------
metrics1 = df[["Model", "Precision", "Recall", "F1-Score"]].melt(id_vars="Model", var_name="Metric", value_name="Score")

plt.figure(figsize=(10, 6))
sns.barplot(data=metrics1, x="Model", y="Score", hue="Metric", palette="Set2")
plt.title("🔍 Precision, Recall, F1-Score (Unsupervised Models)")
plt.ylim(0, 1)
plt.ylabel("Score")
plt.xlabel("Model")
plt.legend(title="Metric", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("plots/unsupervised_fraud_class_metrics.png", bbox_inches="tight")
plt.show()

# -----------------------------
# Plot: ROC-AUC, PR-AUC, Log Loss
# -----------------------------
metrics2 = df[["Model", "ROC-AUC", "PR-AUC", "Log Loss"]].melt(id_vars="Model", var_name="Metric", value_name="Score")

plt.figure(figsize=(10, 6))
sns.barplot(data=metrics2, x="Model", y="Score", hue="Metric", palette="Set1")

# Add score labels on bars
for bar in plt.gca().patches:
    height = bar.get_height()
    plt.gca().text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.005,
        f"{height:.3f}",
        ha='center',
        fontsize=9
    )

plt.title("📊 ROC-AUC, PR-AUC, and Log Loss (Unsupervised Models)")
plt.ylabel("Score")
plt.xlabel("Model")
plt.legend(title="Metric", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("plots/unsupervised_auc_logloss_comparison.png", bbox_inches="tight")
plt.show()