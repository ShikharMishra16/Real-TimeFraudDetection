import pandas as pd
from kafka import KafkaProducer
import json
import time

# Load the dataset
df = pd.read_csv('creditcard.csv')

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Stream the data row by row
for idx, row in df.iterrows():
    producer.send('test-topic', value=row.to_dict())
    print(f"Sent record {idx}")
    time.sleep(1)

producer.flush()
producer.close()
