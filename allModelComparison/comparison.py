import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Load CSVs
auc_logloss = pd.read_csv("supervised_auc_logloss_report.csv")
class_report = pd.read_csv("supervised_classification_report.csv")
unsupervised = pd.read_csv("unsupervised_evaluation.csv")

# -----------------------
# Process Supervised Models
# -----------------------
auc_pivot = auc_logloss.pivot(index='Model', columns='Metric', values='Score').reset_index()
class_weighted = class_report[class_report['index'] == 'weighted avg'].copy()
accuracy_row = class_report[class_report['index'] == 'accuracy']
accuracy_map = dict(zip(accuracy_row['Model'], accuracy_row['precision']))
class_weighted['accuracy'] = class_weighted['Model'].map(accuracy_map)
supervised_df = pd.merge(auc_pivot, class_weighted[['Model', 'precision', 'recall', 'f1-score', 'accuracy']], on='Model')

# Normalize and score
for col in ['ROC-AUC', 'PR-AUC', 'f1-score', 'accuracy', 'Log Loss']:
    if col == 'Log Loss':
        supervised_df['logloss_score'] = 1 - (supervised_df['Log Loss'] / supervised_df['Log Loss'].max())
    else:
        supervised_df[col + '_score'] = supervised_df[col] / supervised_df[col].max()

supervised_df['final_score'] = (
    supervised_df['ROC-AUC_score'] +
    supervised_df['PR-AUC_score'] +
    supervised_df['f1-score_score'] +
    supervised_df['accuracy_score'] +
    supervised_df['logloss_score']
)
supervised_df['Type'] = 'Supervised'

# -----------------------
# Process Unsupervised Models
# -----------------------
unsupervised_df = unsupervised.copy()
for col in ['ROC-AUC', 'PR-AUC', 'F1-Score', 'Log Loss']:
    if col == 'Log Loss':
        unsupervised_df['logloss_score'] = 1 - (unsupervised_df['Log Loss'] / unsupervised_df['Log Loss'].max())
    else:
        unsupervised_df[col + '_score'] = unsupervised_df[col] / unsupervised_df[col].max()

unsupervised_df['final_score'] = (
    unsupervised_df['ROC-AUC_score'] +
    unsupervised_df['PR-AUC_score'] +
    unsupervised_df['F1-Score_score'] +
    unsupervised_df['logloss_score']
)
unsupervised_df['Type'] = 'Unsupervised'

# Align unsupervised for merging
unsupervised_final = unsupervised_df.rename(columns={'F1-Score': 'f1-score'})[
    ['Model', 'Type', 'final_score', 'ROC-AUC', 'PR-AUC', 'f1-score', 'Precision', 'Recall', 'Log Loss']
]
unsupervised_final['accuracy'] = float('nan')

supervised_final = supervised_df[[
    'Model', 'Type', 'final_score', 'ROC-AUC', 'PR-AUC', 'f1-score', 'precision', 'recall', 'Log Loss', 'accuracy'
]]

# Combine all models
final_df = pd.concat([supervised_final, unsupervised_final.reindex(columns=supervised_final.columns)], ignore_index=True)

# -----------------------
# Plot Composite Score
# -----------------------
plt.figure(figsize=(10, 6))
sns.barplot(data=final_df, x='final_score', y='Model', hue='Type', palette='viridis')
plt.title('Model Comparison by Final Composite Score')
plt.xlabel('Composite Score (Normalized)')
plt.ylabel('Model')
plt.legend(title='Model Type')
plt.tight_layout()
plt.show()

# -----------------------
# Plot Metric-Wise Comparison
# -----------------------
metrics = ['ROC-AUC', 'PR-AUC', 'f1-score', 'Log Loss']
for metric in metrics:
    plt.figure(figsize=(10, 5))
    sns.barplot(data=final_df, x=metric, y='Model', hue='Type', palette='coolwarm')
    plt.title(f'Model Comparison by {metric}')
    plt.xlabel(metric)
    plt.ylabel('Model')
    plt.legend(title='Model Type')
    plt.tight_layout()
    plt.show()

# -----------------------
# Best Model
# -----------------------
best_model = final_df.sort_values(by='final_score', ascending=False).iloc[0]
print("\n✅ Best Model Selected:")
print(best_model[['Model', 'Type', 'final_score']])

print("\n🏁 Full Ranked Models:")
print(final_df.sort_values(by='final_score', ascending=False)[['Model', 'Type', 'final_score']])

# -----------------------
# Confusion Matrix Visualization (Optional)
# -----------------------
# You MUST have y_true and y_pred for this to work
# Example: (replace with your own loading logic)
# from joblib import load
# y_true = load("xgboost_y_true.joblib")
# y_pred = load("xgboost_y_pred.joblib")

# Dummy Example — REMOVE and replace with your data
# Only show CM if best model is supervised
if best_model['Type'] == 'Supervised':
    print(f"\n📊 Confusion Matrix for Best Model: {best_model['Model']}")
    # Dummy true/predicted values — replace with actual
    y_true = [0, 0, 1, 1, 0, 1, 0, 0, 1, 1]  # Replace this
    y_pred = [0, 0, 1, 0, 0, 1, 0, 1, 1, 1]  # Replace this

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[0, 1])
    disp.plot(cmap="Blues")
    plt.title(f"Confusion Matrix: {best_model['Model']}")
    plt.tight_layout()
    plt.show()
else:
    print("\n⚠️ Best model is unsupervised — confusion matrix not applicable.")
    
# Save final model scores to CSV
final_df.sort_values(by='final_score', ascending=False).to_csv("final_model_scores.csv", index=False)
print("\n📁 Model scores saved to 'final_model_scores.csv'")
