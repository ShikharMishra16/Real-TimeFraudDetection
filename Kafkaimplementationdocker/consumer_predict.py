import os
from kafka import KafkaConsumer
import json
import pandas as pd
import joblib

model = joblib.load("fraud_detection_model.pkl")

feature_cols = [
    'Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
    'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
    'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 'Amount',
    'Hour', 'Is_Night', 'Txns_In_Hour', 'Amt_vs_HourAvg',
    'Amount_Bin_medium', 'Amount_Bin_high', 'Amount_Bin_very_high'
]

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("📥 Waiting for incoming transactions...")

csv_file = "latest_transactions.csv"

# Initialize the file with headers if not exists
if not os.path.exists(csv_file):
    pd.DataFrame(columns=feature_cols + ['Score', 'Class']).to_csv(csv_file, index=False)

for message in consumer:
    row = message.value
    df = pd.DataFrame([row])

    if 'Class' in df.columns:
        df = df.drop(columns=['Class'])

    df = df[feature_cols]

    prob = model.predict_proba(df)[0][1]
    pred = int(prob > 0.5)

    df['Score'] = prob
    df['Class'] = pred

    # Append to latest_transactions.csv
    df.to_csv(csv_file, mode='a', header=False, index=False)

    print(f"✅ Transaction received → Prediction: {pred} | Score: {prob:.6f}")
    if pred == 1:
        print("🚨 FRAUD ALERT DETECTED!")

