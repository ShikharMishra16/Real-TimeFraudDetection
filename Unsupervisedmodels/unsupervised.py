import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    precision_recall_curve,
    auc,
    log_loss,
    roc_curve
)

# -------------------------------
# 1. Load & Prepare Data
# -------------------------------
df = pd.read_csv("final_preprocessed_creditcard.csv")
X = df.drop(columns=["Class"])
y = df["Class"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train = X_scaled[y == 0]

# -------------------------------
# 2. Train Unsupervised Models
# -------------------------------
iso_forest = IsolationForest(contamination=0.001, random_state=42)
iso_forest.fit(X_train)
y_pred_iso = np.where(iso_forest.predict(X_scaled) == -1, 1, 0)
iso_scores = -iso_forest.decision_function(X_scaled)

ocsvm = OneClassSVM(kernel='rbf', nu=0.001, gamma='auto')
ocsvm.fit(X_train)
y_pred_svm = np.where(ocsvm.predict(X_scaled) == -1, 1, 0)
svm_scores = -ocsvm.decision_function(X_scaled)

# -------------------------------
# 3. Evaluate + Save Results
# -------------------------------
def evaluate_model(y_true, y_pred, raw_scores, model_name):
    norm_scores = MinMaxScaler().fit_transform(raw_scores.reshape(-1, 1)).flatten()
    pr_prec, pr_recall, _ = precision_recall_curve(y_true, norm_scores)
    pr_auc = auc(pr_recall, pr_prec)

    try:
        logloss = log_loss(y_true, norm_scores)
    except:
        logloss = float('nan')

    print(f"\n📊 --- {model_name} ---")
    print("Confusion Matrix:\n", confusion_matrix(y_true, y_pred))
    print("Classification Report:\n", classification_report(y_true, y_pred, digits=4))

    return {
        "Model": model_name,
        "Precision": precision_score(y_true, y_pred),
        "Recall": recall_score(y_true, y_pred),
        "F1-Score": f1_score(y_true, y_pred),
        "ROC-AUC": roc_auc_score(y_true, norm_scores),
        "PR-AUC": pr_auc,
        "Log Loss": logloss,
        "Normalized Scores": norm_scores  # for plotting
    }

results = []
iso_eval = evaluate_model(y, y_pred_iso, iso_scores, "Isolation Forest")
svm_eval = evaluate_model(y, y_pred_svm, svm_scores, "One-Class SVM")
results.append({k: v for k, v in iso_eval.items() if k != "Normalized Scores"})
results.append({k: v for k, v in svm_eval.items() if k != "Normalized Scores"})

results_df = pd.DataFrame(results)
os.makedirs("unsupervised_output", exist_ok=True)
results_df.to_csv("unsupervised_output/unsupervised_evaluation.csv", index=False)
print("\n✅ Saved evaluation CSV to 'unsupervised_output/unsupervised_evaluation.csv'")

# -------------------------------
# 4. Plot ROC and PR Curves
# -------------------------------
def plot_roc_pr_curves(y_true, evals):
    os.makedirs("plots", exist_ok=True)

    # ROC Curve
    plt.figure(figsize=(8, 6))
    for eval in evals:
        fpr, tpr, _ = roc_curve(y_true, eval["Normalized Scores"])
        auc_score = roc_auc_score(y_true, eval["Normalized Scores"])
        plt.plot(fpr, tpr, label=f"{eval['Model']} (AUC = {auc_score:.4f})")
    plt.plot([0, 1], [0, 1], "k--", label="Random Guess")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve (Unsupervised Models)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("unsupervised_roc_curve.png")
    plt.show()

    # PR Curve
    plt.figure(figsize=(8, 6))
    for eval in evals:
        precision, recall, _ = precision_recall_curve(y_true, eval["Normalized Scores"])
        pr_auc = auc(recall, precision)
        plt.plot(recall, precision, label=f"{eval['Model']} (PR-AUC = {pr_auc:.4f})")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve (Unsupervised Models)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("unsupervised_pr_curve.png")
    plt.show()

plot_roc_pr_curves(y, [iso_eval, svm_eval])
