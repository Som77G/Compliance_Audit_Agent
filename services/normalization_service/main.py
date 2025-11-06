from kafka import KafkaConsumer, KafkaProducer
import json
import os
import time

RAW_TOPIC = os.getenv("RAW_TOPIC", "raw_logs")
NORMALIZED_TOPIC = os.getenv("NORMALIZED_TOPIC", "normalized_logs")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

# Connect to Kafka
for _ in range(10):
    try:
        consumer = KafkaConsumer(
            RAW_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            group_id="normalization_service_group",
            auto_offset_reset='latest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Connected to Kafka.")
        break
    except Exception as e:
        print(f"Kafka not ready yet ({e}), retrying...")
        time.sleep(5)
else:
    raise Exception("Kafka broker unavailable.")


# === ECS Normalization Functions ===
def normalize_siem(log):
    return {
        "@timestamp": log.get("timestamp"),
        "event": {
            "category": "security",
            "type": log.get("event_type"),
            "severity": log.get("severity"),
            "action": log.get("event_type")
        },
        "source": {"ip": log.get("src_ip")},
        "destination": {"ip": log.get("dest_ip")},
        "host": {"name": log.get("hostname")},
        "user": {"name": log.get("user")},
        "message": log.get("msg"),
        "ecs": {"version": "8.11.0"},
        "observer": {"vendor": log.get("device_vendor"), "product": log.get("device_product")}
    }


def normalize_edr(log):
    return {
        "@timestamp": log.get("timestamp"),
        "event": {
            "category": "process",
            "type": log.get("event"),
            "severity": log.get("severity")
        },
        "host": {"name": log.get("endpoint_id"), "os": log.get("os")},
        "user": {"name": log.get("user")},
        "process": {
            "name": log.get("process_name"),
            "pid": log.get("process_id"),
            "parent": {"name": log.get("parent_process")}
        },
        "observer": {"vendor": log.get("device_vendor")},
        "ecs": {"version": "8.11.0"}
    }


def normalize_asset_management(log):
    return {
        "@timestamp": log.get("timestamp"),
        "event": {
            "category": "inventory",
            "type": "asset_status"
        },
        "host": {"name": log.get("hostname")},
        "asset": {
            "id": log.get("asset_id"),
            "type": log.get("asset_type"),
            "status": log.get("status"),
            "owner": log.get("owner"),
            "os": log.get("os")
        },
        "vulnerability": {
            "cve": log.get("missing_patches", [])
        },
        "ecs": {"version": "8.11.0"}
    }


def normalize_network_monitoring(log):
    return {
        "@timestamp": log.get("timestamp"),
        "event": {
            "category": "network",
            "type": log.get("protocol"),
            "action": "connection_test"
        },
        "source": {"ip": log.get("src_ip")},
        "destination": {"ip": log.get("dest_ip")},
        "network": {
            "protocol": log.get("protocol"),
            "latency": log.get("latency_ms"),
            "packet_loss": log.get("packet_loss")
        },
        "observer": {"name": log.get("device"), "vendor": log.get("vendor")},
        "ecs": {"version": "8.11.0"}
    }


# === Normalization Router ===
def normalize_log(log):
    source = log.get("source_type")
    if source == "siem":
        return normalize_siem(log)
    elif source == "edr":
        return normalize_edr(log)
    elif source == "asset_management":
        return normalize_asset_management(log)
    elif source == "network_monitoring":
        return normalize_network_monitoring(log)
    else:
        print(f"Unknown source_type: {source}")
        return None


# === Kafka Consumer Loop ===
print("Listening for logs...")
for message in consumer:
    raw_log = message.value
    normalized = normalize_log(raw_log)

    if normalized:
        producer.send(NORMALIZED_TOPIC, normalized)
        print(f"Normalized and sent log from {raw_log['source_type']}")
    else:
        print("Skipped log, no normalization rule found.")
