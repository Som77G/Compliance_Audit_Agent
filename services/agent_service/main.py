from kafka import KafkaConsumer, KafkaProducer
import json
import os
from utils.llm_agent import generate_audit_statement
from utils.compliance_checker import check_compliance

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

consumer = KafkaConsumer(
    'normalized_logs',
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Agent service started and listening on topic: normalized_logs")

for msg in consumer:
    normalized_log = msg.value

    print("Received normalized log:", normalized_log)

    # Step 1: Generate audit statement
    audit_statement = generate_audit_statement(normalized_log)

    # Step 2: Check compliance
    compliance_result = check_compliance(audit_statement)

    # Step 3: Publish result
    output = {
        "audit_statement": audit_statement,
        "compliance_result": compliance_result
    }
    producer.send("audit_results", value=output)
    print("Processed →", output)
