import os
import google.generativeai as genai
from chromadb import Client
from PyPDF2 import PdfReader

# Load Gemini API key from environment
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Chroma client and collection
chroma_client = Client()
collection = chroma_client.get_or_create_collection(name="audit_docs")

# Path to folder containing your compliance PDFs
PDF_FOLDER = "services/agent_service/vector_db/compliance_docs"


def extract_text_from_pdf(pdf_path: str) -> str:
    """Reads and concatenates text from all pages in a PDF."""
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text.strip()


def embed_policies_from_folder(folder_path=PDF_FOLDER):
    """Embeds all PDFs in a given folder and stores them in ChromaDB."""
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    # Get list of already-embedded IDs to avoid duplicates
    existing_docs = collection.get()["ids"] if collection.count() > 0 else []
    embedded_count = 0

    for filename in os.listdir(folder_path):
        if not filename.endswith(".pdf"):
            continue
        if filename in existing_docs:
            print(f"⏭Skipping {filename}: already embedded.")
            continue

        pdf_path = os.path.join(folder_path, filename)
        print(f"\nProcessing: {filename}")

        # Extract text
        text = extract_text_from_pdf(pdf_path)
        if not text:
            print(f"Skipping {filename}: empty or unreadable.")
            continue

        # Generate embedding using Gemini
        try:
            response = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            embedding = response["embedding"]
        except Exception as e:
            print(f"Embedding failed for {filename}: {e}")
            continue

        # Add to ChromaDB
        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[filename]
        )

        embedded_count += 1
        print(f"Embedded and stored: {filename}")

    print(f"\nEmbedding complete. {embedded_count} new documents added.")


if __name__ == "__main__":
    print("Starting PDF embedding process...")
    embed_policies_from_folder()
    print("All policies embedded successfully!\n")
