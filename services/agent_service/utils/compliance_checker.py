from utils.embeddings import retrieve_relevant_docs
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Configure Gemini API key
google_api_key = os.getenv("GOOGLE_API_KEY")

# Initialize model for generating text
model = ChatGoogleGenerativeAI(model = "gemini-2.0-flash", google_api_key = google_api_key)

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
        "is_compliant": compliant/ partially-compliant/ non-compliant,
        "reason": "short explanation"
    }}
    """

    response = model.invoke(prompt)
    return response.text.strip()
