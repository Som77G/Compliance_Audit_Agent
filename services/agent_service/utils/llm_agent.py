import google.generativeai as genai
import os

# Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize model for generating text
model = genai.GenerativeModel("models/gemini-2.0-flash-lite")

def generate_audit_statement(normalized_log: dict) -> str:
    """
    Converts a normalized log into a human-readable audit statement
    using Gemini 2.5 Pro.
    """
    prompt = f"""
    You are an audit assistant. Convert the following normalized log into a clear, concise audit statement.

    Example:
    Input: {{
        "@timestamp": "2025-10-29T10:00:00Z",
        "event": {{"type": "file_modified", "severity": "medium"}},
        "user": {{"name": "root"}},
        "message": "Critical system file modified: /etc/passwd"
    }}
    Output: "Root user modified the critical system file /etc/passwd on October 29, 2025."

    Now convert this log:
    {normalized_log}
    """

    response = model.generate_content(prompt)
    return response.text.strip()
