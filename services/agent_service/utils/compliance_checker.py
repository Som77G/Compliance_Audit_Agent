from utils.embeddings import retrieve_relevant_docs
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use Gemini 2.5 Pro for compliance reasoning
model = genai.GenerativeModel("models/gemini-2.0-flash-lite")

def check_compliance(audit_statement: str):
    """
    Determines compliance of the given audit statement
    based on context from retrieved policy documents.
    """
    context_docs = retrieve_relevant_docs(audit_statement)

    prompt = f"""
    You are a compliance auditor. Based on the following reference documents,
    determine if the described audit action is compliant or not.

    Context Documents:
    {context_docs}

    Audit Statement:
    {audit_statement}

    Respond in strict JSON format:
    {{
        "is_compliant": true or false,
        "reason": "short explanation"
    }}
    """

    response = model.generate_content(prompt)
    return response.text.strip()
