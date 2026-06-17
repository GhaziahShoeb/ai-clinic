import chromadb
import os
from groq import Groq

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="patient_records")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_embedding(text: str):
    # use a simple hash-based approach for now
    # Groq doesn't have embeddings API yet, so we use a lightweight approach
    words = text.lower().split()
    vector = [hash(word) % 1000 / 1000.0 for word in words[:384]]
    vector += [0.0] * (384 - len(vector))
    return vector

def embed_patient(patient_id: int, text: str):
    embedding = get_embedding(text)
    collection.upsert(
        ids=[str(patient_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"patient_id": patient_id}]
    )

def search_similar(patient_id: int, query: str, n_results: int = 3):
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        where={"patient_id": patient_id},
        n_results=n_results
    )
    return results['documents'][0] if results['documents'] else []