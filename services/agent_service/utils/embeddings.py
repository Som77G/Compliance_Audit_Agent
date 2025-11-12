from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import chromadb

# Configure Gemini
google_api_key = os.getenv("GOOGLE_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=google_api_key
)

def retrieve_relevant_docs(query_text: str):
    """
    Generates an embedding for the given query using Gemini embeddings API
    and retrieves top related compliance documents from ChromaDB.
    """
    CHROMA_DB_PATH = "/app/vector_db/chroma_store"

    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = chroma_client.get_or_create_collection(name="audit_docs")

    # Generate embedding
    query_embedding = embeddings.embed_query(query_text)
    print("Embedding generated out of Audit Statement\n")

    # Query ChromaDB for relevant documents
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    docs = [doc for sublist in results.get("documents", []) for doc in sublist]
    print("Relevant docs extracted:", docs)

    return "\n".join(docs) if docs else "No relevant documents found."
