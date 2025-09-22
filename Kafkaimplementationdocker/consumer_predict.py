import json
import joblib
import pandas as pd
from kafka import KafkaConsumer
import numpy as np

# Load the trained model
try:
    model = joblib.load("fraud_detection_model.pkl")
    print("[INFO] Model loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    exit(1)

# Kafka consumer setup
try:
    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print("[INFO] Connected to Kafka topic.")
except Exception as e:
    print(f"[ERROR] Kafka connection failed: {e}")
    exit(1)

def feature_engineering(df):
    df['Hour'] = (df['Time'] // 3600) % 24
    df['Is_Night'] = df['Hour'].apply(lambda x: 1 if (x >= 0 and x <= 6) else 0)
    
    df['Txns_In_Hour'] = df.groupby('Hour')['Hour'].transform('count')
    df['Amt_vs_HourAvg'] = df['Amount'] / (df.groupby('Hour')['Amount'].transform('mean') + 1e-5)

    # Binning Amount
    df['Amount_Bin'] = pd.cut(df['Amount'], bins=[-1, 50, 200, 1000, float('inf')],
                              labels=['low', 'medium', 'high', 'very_high'])
    df = pd.get_dummies(df, columns=['Amount_Bin'])

    # Add missing dummy columns if any (needed to match model input)
    for col in ['Amount_Bin_low', 'Amount_Bin_medium', 'Amount_Bin_high', 'Amount_Bin_very_high']:
        if col not in df.columns:
            df[col] = 0

    return df

# Stream and predict
for message in consumer:
    try:
        record = message.value
        df = pd.DataFrame([record])

        if 'Class' in df.columns:
            df = df.drop('Class', axis=1)

        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
        df = feature_engineering(df)

        # Keep only features the model trained on
        model_features = model.feature_names_in_
        df = df.reindex(columns=model_features, fill_value=0)

        prediction = model.predict(df)[0]
        label = "Fraud" if prediction == 1 else "Not Fraud"
        print(f"[+] Received Record with Prediction: {label}")

    except Exception as e:
        print(f"[ERROR] Failed to process record: {e}")
