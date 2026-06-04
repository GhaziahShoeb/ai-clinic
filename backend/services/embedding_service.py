from sentence_transformers import SentenceTransformer
import chromadb
import os

# Load Bio_ClinicalBERT model
model = SentenceTransformer('emilyalsentzer/Bio_ClinicalBERT')

# Create ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create collection
collection = chroma_client.get_or_create_collection(
    name="patient_records"
)

def embed_patient(patient_id: int, text: str):
    embedding = model.encode(text).tolist()

    collection.upsert(
        ids=[str(patient_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"patient_id": patient_id}]
    )

def search_similar(patient_id: int, query: str, n_results: int = 3):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        where={"patient_id": patient_id},
        n_results=n_results
    )

    return results["documents"][0] if results["documents"] else []
