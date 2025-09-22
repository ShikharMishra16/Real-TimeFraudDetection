import streamlit as st
import pandas as pd
import json
import joblib
from kafka import KafkaConsumer

st.set_page_config(page_title="Fraud Detection", layout="wide")

st.markdown("<h1 style='text-align: center;'>💳 Real-time Fraud Detection Monitor</h1>", unsafe_allow_html=True)
st.markdown("---")

@st.cache_resource
def load_model():
    return joblib.load("fraud_detection_model.pkl")

model = load_model()

placeholder = st.empty()

# Kafka Consumer
consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def feature_engineering(df):
    df['Hour'] = (df['Time'] // 3600) % 24
    df['Is_Night'] = df['Hour'].apply(lambda x: 1 if (x >= 0 and x <= 6) else 0)
    df['Txns_In_Hour'] = df.groupby('Hour')['Hour'].transform('count')
    df['Amt_vs_HourAvg'] = df['Amount'] / (df.groupby('Hour')['Amount'].transform('mean') + 1e-5)
    df['Amount_Bin'] = pd.cut(df['Amount'], bins=[-1, 50, 200, 1000, float('inf')],
                              labels=['low', 'medium', 'high', 'very_high'])
    df = pd.get_dummies(df, columns=['Amount_Bin'])

    for col in ['Amount_Bin_low', 'Amount_Bin_medium', 'Amount_Bin_high', 'Amount_Bin_very_high']:
        if col not in df.columns:
            df[col] = 0

    return df

predictions = []

# Main Loop
for message in consumer:
    record = message.value
    df = pd.DataFrame([record])

    if 'Class' in df.columns:
        df = df.drop('Class', axis=1)

    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    df = feature_engineering(df)

    model_features = model.feature_names_in_
    df = df.reindex(columns=model_features, fill_value=0)

    prediction = model.predict(df)[0]
    label = "Fraud" if prediction == 1 else "Not Fraud"

    record['Prediction'] = label
    predictions.append(record)

    latest_df = pd.DataFrame(predictions)
    placeholder.dataframe(latest_df.tail(10), use_container_width=True)
