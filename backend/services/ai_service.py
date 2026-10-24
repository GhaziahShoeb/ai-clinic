from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from services.embedding_service import search_similar
from core.config import settings

def _get_llm():
    try:
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.startswith("gsk_"):
            return ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model_name="llama-3.3-70b-versatile"
            )
    except Exception:
        pass
    return None

def ask_about_patient(patient_id: int, question: str) -> str:
    """
    RAG pipeline:
    1. Search ChromaDB for relevant patient record chunks
    2. Build a prompt with those chunks as context
    3. Send to Groq LLM (with fallback if API key is invalid)
    4. Return answer
    """
    relevant_chunks = search_similar(patient_id, question, n_results=3)

    if not relevant_chunks:
        return "No patient records found. Please make sure the patient record has been embedded first."

    context = "\n\n".join(relevant_chunks)

    try:
        llm = _get_llm()
        if llm:
            messages = [
                SystemMessage(content="""You are a clinical assistant helping doctors 
                answer questions about their patients. Answer based only on the provided 
                patient record. Be concise and cite specific details from the record."""),

                HumanMessage(content=f"""Patient Record:
{context}

Doctor's Question: {question}

Answer based only on the patient record above:""")
            ]
            response = llm.invoke(messages)
            return response.content
    except Exception as err:
        print(f"Groq API call failed: {err}")

    # Fallback if Groq API key is invalid
    return f"""Clinical Details:
{context.strip()}

(Note: To enable generative AI responses, please provide a valid GROQ_API_KEY in backend/.env)"""

def generate_patient_summary(patient_id: int) -> str:
    """
    Generate a one-click AI summary of a patient's record
    covering: chief complaint, conditions, medications, allergies, recent notes
    """
    relevant_chunks = search_similar(patient_id, "patient summary conditions medications allergies notes", n_results=3)

    if not relevant_chunks:
        return "No patient records found. Please embed the patient record first."

    context = "\n\n".join(relevant_chunks)

    try:
        llm = _get_llm()
        if llm:
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
    except Exception as err:
        print(f"Groq API call failed: {err}")

    # Clean structured fallback if Groq API key is invalid
    return f"""📋 Clinical Record Summary:
{context.strip()}

⚠️ Note: Groq API key is invalid or expired. To enable AI-generated summaries, add a valid key from https://console.groq.com/keys into backend/.env."""
