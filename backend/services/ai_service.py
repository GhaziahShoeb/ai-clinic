from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from services.embedding_service import search_similar
from core.config import settings

# initialize Groq LLM — runs on Groq's servers, not your Mac
llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile"
)

def ask_about_patient(patient_id: int, question: str) -> str:
    """
    RAG pipeline:
    1. Search ChromaDB for relevant patient record chunks
    2. Build a prompt with those chunks as context
    3. Send to Groq LLM
    4. Return answer with citations
    """

    # step 1 — retrieve relevant chunks from ChromaDB
    relevant_chunks = search_similar(patient_id, question, n_results=3)

    if not relevant_chunks:
        return "No patient records found. Please make sure the patient record has been embedded first."

    # step 2 — build context from retrieved chunks
    context = "\n\n".join(relevant_chunks)

    # step 3 — build prompt
    messages = [
        SystemMessage(content="""You are a clinical assistant helping doctors 
        answer questions about their patients. Answer based only on the provided 
        patient record. Be concise and cite specific details from the record."""),

        HumanMessage(content=f"""Patient Record:
{context}

Doctor's Question: {question}

Answer based only on the patient record above:""")
    ]

    # step 4 — send to Groq and return response
    response = llm.invoke(messages)
    return response.content

def generate_patient_summary(patient_id: int) -> str:
    """
    Generate a one-click AI summary of a patient's record
    covering: chief complaint, conditions, medications, allergies, recent notes
    """
    relevant_chunks = search_similar(patient_id, "patient summary conditions medications allergies notes", n_results=3)

    if not relevant_chunks:
        return "No patient records found. Please embed the patient record first."

    context = "\n\n".join(relevant_chunks)

    messages = [
        SystemMessage(content="""You are a clinical assistant. Generate a concise 
        structured summary of the patient record. Include:
        - Conditions
        - Current medications
        - Known allergies
        - Key clinical notes
        Be brief and clinical."""),

        HumanMessage(content=f"""Patient Record:
{context}

Generate a structured clinical summary:""")
    ]

    response = llm.invoke(messages)
    return response.content
