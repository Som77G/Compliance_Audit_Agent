FROM python:3.11-slim

WORKDIR /app

# Copy your Python files
COPY . .

# Install dependencies (kafka-python, pandas, PyPDF2)
RUN pip install --no-cache-dir \
    kafka-python \
    pandas \
    PyPDF2

# Run the producer
CMD ["python", "main.py"]
