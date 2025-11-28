# kafka_producer.py
from kafka import KafkaProducer
import pandas as pd
import time
import json

# Load the correct test dataset
df = pd.read_csv("test_frauds2.csv")

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

for _, row in df.iterrows():
    producer.send("transactions", value=row.to_dict())
    print("Sent:", row.to_dict())
    time.sleep(1)

print("All test frauds sent.")

