FROM python:3.11-slim

WORKDIR /app

# Copy your Python files
COPY . .

# Install dependencies (kafka-python)
RUN pip install --no-cache-dir kafka-python

# Run the producer
CMD ["python", "main.py"]
