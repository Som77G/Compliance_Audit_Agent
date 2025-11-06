import os
import json
import time
import pandas as pd
from kafka import KafkaProducer
from PyPDF2 import PdfReader

# Kafka Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "raw_logs")

LOG_DIR = "periodic_data"  # folder where your files exist

CATEGORY_MAP = {
    "siem": "siem",
    "edr": "edr",
    "patch": "asset_management",
    "asset": "asset_management",
    "network": "network_monitoring",
    "monitor": "network_monitoring"
}

def detect_key(filename):
    """Infer log type from filename."""
    name = filename.lower()
    for key, value in CATEGORY_MAP.items():
        if key in name:
            return value
    return "unknown"

def read_txt(path):
    logs = []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return logs

def read_csv(path):
    df = pd.read_csv(path).fillna("")
    return df.to_dict(orient="records")

def read_pdf(path):
    logs = []
    reader = PdfReader(path)
    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue
        for line in text.split("\n"):
            line = line.strip()
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return logs

def collect_logs():
    """Collect and flatten all logs with their type tag."""
    aggregated = []

    for file in os.listdir(LOG_DIR):
        path = os.path.join(LOG_DIR, file)
        if not os.path.isfile(path):
            continue

        source_type = detect_key(file)

        if file.endswith(".txt"):
            logs = read_txt(path)
        elif file.endswith(".csv"):
            logs = read_csv(path)
        elif file.endswith(".pdf"):
            logs = read_pdf(path)
        else:
            continue

        # Add type field to each entry
        for entry in logs:
            entry["type"] = source_type  # ✅ explicit category field
            aggregated.append(entry)

    return aggregated

# ✅ CONNECT TO KAFKA WITH RETRIES
for i in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print("✅ Connected to Kafka broker!")
        break
    except Exception as e:
        print(f"⚠️ Kafka not ready yet ({e}), retrying in 5s...")
        time.sleep(5)
else:
    raise Exception("❌ Kafka broker not available after 10 retries.")

print("📂 Reading logs from periodic_data/ ...")
logs = collect_logs()
print(f"✅ Total logs collected: {len(logs)}")

# ✅ SEND LOGS ONE BY ONE (STREAM MODE)
for log in logs:
    producer.send(TOPIC_NAME, value=log)
    print(f"📤 Sent log → {log.get('type')} | {log.get('timestamp', 'no-timestamp')}")
    time.sleep(1)  # simulate stream

producer.flush()
print("\n🎯 All logs sent successfully to Kafka topic:", TOPIC_NAME)
