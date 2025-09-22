import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    classification_report, roc_auc_score, log_loss,
    precision_recall_curve, roc_curve, auc
)
import joblib
import os

# -----------------------------------------
# 1. Load Data
# -----------------------------------------
df = pd.read_csv("final_preprocessed_creditcard.csv")
X = df.drop('Class', axis=1)
y = df['Class']

# -----------------------------------------
# 2. Train/Test Split
# -----------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# -----------------------------------------
# 3. Train Models
# -----------------------------------------
lr = LogisticRegression(class_weight='balanced', max_iter=3000, solver='lbfgs', random_state=42)
lr.fit(X_train, y_train)

rf = RandomForestClassifier(n_estimators=10, class_weight='balanced', random_state=42)
rf.fit(X_train, y_train)

scale = len(y_train[y_train == 0]) / len(y_train[y_train == 1])
xgb = XGBClassifier(scale_pos_weight=scale, eval_metric='logloss', random_state=42)
xgb.fit(X_train, y_train)

# -----------------------------------------
# 4. Evaluation
# -----------------------------------------
def get_metrics(model, name):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, y_pred, output_dict=True)
    df_report = pd.DataFrame(report).transpose().reset_index()
    df_report.insert(0, "Model", name)

    roc = roc_auc_score(y_test, y_proba)
    logloss = log_loss(y_test, y_proba)
    precision, recall, _ = precision_recall_curve(y_test, y_proba)
    pr_auc = auc(recall, precision)

    extra = pd.DataFrame({
        "Model": [name] * 3,
        "Metric": ["ROC-AUC", "Log Loss", "PR-AUC"],
        "Score": [roc, logloss, pr_auc]
    })

    return df_report, extra, (y_proba, roc, precision, recall, pr_auc)

# Evaluate
lr_report, lr_extra, lr_curves = get_metrics(lr, "Logistic Regression")
rf_report, rf_extra, rf_curves = get_metrics(rf, "Random Forest")
xgb_report, xgb_extra, xgb_curves = get_metrics(xgb, "XGBoost")

# Save reports
pd.concat([lr_report, rf_report, xgb_report]).to_csv("supervised_classification_report.csv", index=False)
pd.concat([lr_extra, rf_extra, xgb_extra]).to_csv("supervised_auc_logloss_report.csv", index=False)
print("✅ Metrics saved to CSVs")

# -----------------------------------------
# 5. Plot ROC & PR Curves
# -----------------------------------------
def plot_roc_pr(model_curves):
    plt.figure(figsize=(14, 6))

    # ROC
    plt.subplot(1, 2, 1)
    for name, (y_proba, roc_auc, precision, recall, pr_auc) in model_curves:
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.title("ROC Curve")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()

    # PR
    plt.subplot(1, 2, 2)
    for name, (y_proba, roc_auc, precision, recall, pr_auc) in model_curves:
        plt.plot(recall, precision, label=f"{name} (PR AUC = {pr_auc:.4f})")
    plt.title("Precision-Recall Curve")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend()

    plt.tight_layout()
    plt.show()

plot_roc_pr([
    ("Logistic Regression", lr_curves),
    ("Random Forest", rf_curves),
    ("XGBoost", xgb_curves)
])

# -----------------------------------------
# 6. Save Trained Models to `models/`
# -----------------------------------------
os.makedirs("models", exist_ok=True)

# Save the best and other models
joblib.dump(xgb, "models/fraud_detection_model.pkl")             # Best model
joblib.dump(rf, "models/random_forest_model.pkl")                # Random Forest
joblib.dump(lr, "models/logistic_regression_model.pkl")         # Logistic Regression

# If you used a scaler (like StandardScaler), save it here too:
# joblib.dump(scaler, "models/scaler.pkl")                      # Uncomment if scaler is used

print("✅ All models saved in 'models/' folder")
