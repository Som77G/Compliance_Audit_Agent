from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/fetch-data")

# fetch from database the organizations for which auditing needs to be done.

def fetch_data():
    # simple static sample response to prove orchestration
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "orgs": [
            {
                "org_id": "org123",
                "files": [
                    "s3://example-bucket/org123/file1.csv",
                    "s3://example-bucket/org123/file2.csv"
                ]
            }
        ]
    }
