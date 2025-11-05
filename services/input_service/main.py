from kafka import KafkaProducer
import json
import time
import os

# Kafka configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "raw_logs")

# Create producer with serializer
for i in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Convert dict → bytes
        )
        print("Connected to Kafka broker!")
        break
    except Exception as e:
        print(f"Kafka not ready yet ({e}), retrying in 5s...")
        time.sleep(5)
else:
    raise Exception("Kafka broker not available after 10 retries.")

# Read sample logs
data_path = os.path.join(os.path.dirname(__file__), "data/sample_logs.json")
with open(data_path) as f:
    logs = json.load(f)

print("Fetched demo logs")

# Send logs one by one
for source, entries in logs.items():
    for log in entries:
        log["source_type"] = source
        producer.send(TOPIC_NAME, value=log)
        print(f"Sent log from {source}: {log['timestamp']}")
        time.sleep(1.5)  # simulate streaming delay

producer.flush()
print("\nAll logs sent successfully!")
