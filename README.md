# AI-Driven Agentic RAG Platform for Cybersecurity Compliance & Audit Automation

## Overview

This project implements an **AI-driven Agentic Retrieval-Augmented Generation (RAG) platform** to automate cybersecurity compliance monitoring and audit management.

The system continuously ingests security telemetry, normalizes heterogeneous logs, reasons over regulatory knowledge using Large Language Models (LLMs), and produces **explainable, evidence-backed compliance verdicts**.

Unlike traditional rule-based compliance tools, this platform integrates:

- Real-time log ingestion
- LLM-powered contextual reasoning
- Vector-based regulatory knowledge retrieval
- Agent-based workflow orchestration

The result is a **scalable, modular, and intelligent compliance automation system** aligned with modern cybersecurity environments.

---

## Key Features

- Continuous ingestion of SIEM, EDR, network, and asset management logs  
- Kafka-based event-driven microservice architecture  
- ECS-compliant log normalization  
- LLM-generated human-readable audit statements  
- RAG-based compliance reasoning using ChromaDB  
- Google Gemini LLM and embeddings integration  
- Modular agent services with fault tolerance  
- Evidence-backed compliance verdicts in JSON format  

---

## System Architecture

The platform is composed of the following microservices:

- Telemetry Input Service  
- Periodic Input Service  
- Normalization Service  
- Agent Service  
- Vector Knowledge Base (ChromaDB)  
- Kafka Message Broker  

All services communicate asynchronously via **Kafka topics**, ensuring loose coupling and scalability.

---

## Technology Stack

- **Programming Language:** Python 3.11  
- **Message Broker:** Apache Kafka  
- **LLM:** Google Gemini (2.0 Flash / Flash Lite)  
- **Embeddings:** Gemini `text-embedding-004`  
- **Vector Database:** ChromaDB  
- **PDF Processing:** PyPDF2  
- **File Monitoring:** Watchdog  
- **Containerization:** Docker & Docker Compose  

---

## Service Breakdown

### 1. Telemetry Input Service

- Acts as the entry point for raw cybersecurity telemetry  
- Uses file watchers to monitor JSON log buffers  
- Detects newly appended logs and pushes them to Kafka  
- Simulates real-time ingestion behavior  

**Output Topic:** `raw_logs`

---

### 2. Periodic Input Service

- Simulates scheduled log ingestion  
- Useful for batch-based or time-driven compliance checks  
- Pushes telemetry logs to Kafka  

---

### 3. Normalization Service

- Consumes raw logs from Kafka  
- Converts heterogeneous logs into ECS-compliant normalized format  
- Standardizes fields across SIEM, EDR, asset, and network logs  

**Input Topic:** `raw_logs`  
**Output Topic:** `normalized_logs`

---

### 4. Agent Service

The Agent Service performs intelligent audit reasoning in multiple steps:

#### a. Audit Statement Generation
- Uses Gemini LLM to convert normalized logs into human-readable audit statements  

#### b. Regulatory Context Retrieval (RAG)
- Generates embeddings for audit statements  
- Retrieves relevant regulatory clauses from ChromaDB  

#### c. Compliance Reasoning
- Uses Gemini LLM to assess compliance  
- Produces structured JSON verdicts with explanations  

**Input Topic:** `normalized_logs`  
**Output Topic:** `audit_results`

---

## Vector Knowledge Base

### Document Processing Pipeline

Compliance PDFs (ISO 27001, NIST 800-53, CERT-In) are stored in:
`services/agent_service/vector_db/compliance_docs`

Processing steps:

1. Text extraction using PyPDF2  
2. Large documents split into batches (~8000 characters)  
3. Gemini LLM segments text into meaningful compliance clauses  
4. Each segment is embedded and stored in ChromaDB  

---

### Embedding Characteristics

- **Model:** `text-embedding-004`  
- Sentence / paragraph-level semantic embeddings  
- Metadata stored for traceability (document name, segment index)  

---

### ChromaDB Persistence (Important)

ChromaDB runs embedded inside the agent container.  
To ensure embeddings persist across restarts:

- Use a persistent ChromaDB client  
- Mount a volume for the ChromaDB directory  

If embeddings appear empty during retrieval, ensure:

- The same ChromaDB path is used for both embedding and querying  
- The agent container is running during queries  
- Embedding was executed inside the same container  

---

## Running the Project

### Prerequisites

- Docker & Docker Compose  
- Google Gemini API Key  



### Environment Variables

Create a `.env` file in the project root:

`GOOGLE_API_KEY=your_api_key_here`




### Start the System
`docker compose up --build`




### Run Embedding (One-Time)

Execute inside the running agent container:

`docker compose exec agent_service python /app/vector_db/embed_docs.py`


This should be run **only once**, unless compliance documents are modified.

---

## Kafka Topics

| Topic Name        | Description                     |
|------------------|---------------------------------|
| raw_logs         | Raw telemetry logs               |
| normalized_logs  | ECS-normalized logs              |
| audit_results    | Compliance verdicts              |

---

## Sample Compliance Output

```json
{
  "audit_statement": "Root user on host sec-srv-1 modified the critical system file /etc/passwd from IP address 10.0.0.8 to 10.0.0.15 on November 4, 2025.",
  "compliance_result": {
    "is_compliant": "non-compliant",
    "reason": "Modifying /etc/passwd suggests potential unauthorized access and violates access control policies."
  }
}
```

---

## Design Highlights

- Event-driven, non-blocking architecture
- Agent-based reasoning instead of static rules
- Explainable AI outputs with evidence traceability
- Modular services for easy extension (remediation, reporting agents)

---

## Future Enhancements

- Persistent standalone ChromaDB service
- Multi-framework compliance mapping
- Confidence scoring per compliance control
- SOAR integration for automated remediation
- Human-in-the-loop approval workflows
- Compliance monitoring and visualization dashboard

---

## License

This project is intended for educational and research purposes.


