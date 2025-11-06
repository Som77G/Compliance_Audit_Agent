import google.generativeai as genai
import os
from chromadb import Client

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def retrieve_relevant_docs(query_text: str):
    """
    Generates an embedding for the given query using Gemini embeddings API
    and retrieves top related compliance documents from ChromaDB.
    """

    chroma_client = Client()
    collection = chroma_client.get_or_create_collection(name="audit_docs")

    # Generate embeddings using Gemini
    embedding_response = genai.embed_content(
        model="models/text-embedding-004",
        content=query_text,
        task_type="retrieval_query"
    )
    query_embedding = embedding_response["embedding"]

    # Query ChromaDB for relevant documents
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    # Combine top retrieved docs as context
    docs = [doc for sublist in results["documents"] for doc in sublist]

    print("Relevant docs extracted: ", docs)
    return "\n".join(docs)
