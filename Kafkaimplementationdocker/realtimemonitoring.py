import pandas as pd
import joblib
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sklearn.ensemble import RandomForestClassifier

# Load trained model and scaler
model = joblib.load("random_forest_model.pkl")
scaler = joblib.load("models/scaler.pkl")  # Optional, if used in training

# Alerting system: sends email on high-risk transactions
def send_alert(transaction_details):
    sender_email = "your_email@gmail.com"
    receiver_email = "recipient_email@gmail.com"
    password = "your_email_password"

    subject = "🚨 Fraud Alert: Suspicious Transaction Detected"
    body = f"""
    High-risk transaction detected:

    {transaction_details}

    Please review immediately.
    """

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("✔️ Alert sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

# Simulate real-time streaming from CSV
stream_data = pd.read_csv("final_preprocessed_creditcard.csv")
batch_size = 10

print("📡 Starting real-time fraud monitoring...\n")

for i in range(0, len(stream_data), batch_size):
    batch = stream_data.iloc[i:i+batch_size].copy()
    ids = batch.index.tolist()
    X_batch = batch.drop(columns=["Class"], errors='ignore')

    # Apply scaler if it exists
    try:
        X_scaled = scaler.transform(X_batch)
    except:
        X_scaled = X_batch

    predictions = model.predict(X_scaled)
    frauds = batch[predictions == 1]

    if not frauds.empty:
        for idx, row in frauds.iterrows():
            print(f"⚠️ Fraud detected in transaction ID {idx}: Amount ${row['Amount']:.2f}")
            send_alert(row.to_dict())
    else:
        print(f"✅ Batch {i//batch_size+1}: No fraud detected.")

    time.sleep(1.5)  # Simulate delay in stream

print("\n📊 Monitoring complete.")


