import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the root directory to sys.path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.vector_store import VectorStoreManager
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Page Config
st.set_page_config(page_title="Healthcare RAG (Local)", page_icon="🏥", layout="wide")

# Title and Header
st.title("🏥 Healthcare RAG Assistant (Gemini Pro)")
st.markdown("Ask questions about clinical guidelines, drug info, and patient records. Powered by **FAISS** and **Google Gemini Pro**.")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # Check for Index
    index_exists = os.path.exists("faiss_index/index.faiss")
    if index_exists:
        st.success("✅ Knowledge Base Loaded")
    else:
        st.error("❌ Knowledge Base Not Found")
        st.info("Please run the data ingestion pipeline first.")
        
    st.divider()
    
    # Check for Google API Key
    if "GOOGLE_API_KEY" not in os.environ:
        st.error("❌ GOOGLE_API_KEY not found in environment variables.")
        st.info("Please set GOOGLE_API_KEY in your .env file.")
        st.stop()
    else:
        st.success("✅ Gemini Pro API Key Confiigured")

    st.divider()
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF/TXT/CSV/MD", type=["txt", "pdf", "md", "csv", "json"])
    if uploaded_file:
        if st.button("Ingest Document"):
            with st.spinner("Processing..."):
                # Save to temp file
                save_dir = "data/patient_uploads"
                os.makedirs(save_dir, exist_ok=True)
                file_path = os.path.join(save_dir, uploaded_file.name)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Ingest
                # Import here to avoid circular dependencies if any, or just use the module
                from rag.ingest import ingest_file
                success, msg = ingest_file(file_path)
                
                if success:
                    st.success(f"Ingested! {msg}")
                else:
                    st.error(f"Error: {msg}")

    st.divider()
    with st.expander("Connect Google Drive"):
        st.markdown("Ingest files directly from a Drive folder.")
        folder_id = st.text_input("Folder ID", help="The ID from the Google Drive URL")
        if st.button("Start Drive Ingestion"):
            if not folder_id:
                st.warning("Please enter a Folder ID.")
            else:
                with st.spinner("Connecting to Drive (Authentication may open in browser)..."):
                    try:
                        from rag.drive_ingest import ingest_from_drive_folder
                        success, msg = ingest_from_drive_folder(folder_id)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    except ImportError:
                        st.error("Google Drive dependencies not installed. Run `pip install -r requirements.txt`.")
                    except Exception as e:
                        st.error(f"Error: {e}")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# RAG Logic
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@st.cache_resource
def get_vector_store():
    return VectorStoreManager().load_vector_store()

def get_answer(question):
    # 1. Retrieval
    try:
        vector_store = get_vector_store()
        # Increased k to 10 to capture more sources (including user uploads)
        retriever = vector_store.as_retriever(search_kwargs={"k": 10})
        docs = retriever.invoke(question)
    except Exception as e:
        return f"Error loading knowledge base: {e}", []

    context_text = format_docs(docs)
    
    # 2. Generation (Gemini)
    template = """You are a comprehensive Healthcare Assistant. Your role is to answer ANY health-related question based on the medical knowledge base provided.

**YOU CAN ANSWER QUESTIONS ABOUT:**
- Medical conditions and diseases
- Symptoms and causes
- Medications and treatments
- Lab test results and reference ranges
- General health and wellness
- Medical reports and terminology

**IMPORTANT GUIDELINES:**
- **Medical Report Analysis**: If the user provides a report (or one is retrieved), analyze the values against reference ranges.
- **Data Sources**: Prioritize information from user-uploaded documents (e.g., Mayo Clinic PDFs) if relevant.
- **Lab Values**: Always mention reference ranges if available in the context.
- **Safety**: DO NOT diagnose or treat. If uncertain, advise consulting a doctor.

**Context (Retrieved Medical Knowledge):**
{context}

**User Question:**
{question}

**Answer:**
Provide a detailed, educational answer. Include specific data points (like normal ranges) from the context if relevant.
    
**Disclaimer:**
This information is for educational purposes only and does not constitute medical advice. Please consult with your healthcare provider for personalized medical guidance.
"""
    prompt = ChatPromptTemplate.from_template(template)
    
    try:
        model = ChatGoogleGenerativeAI(model="gemini-flash-latest", convert_system_message_to_human=True)
        
        chain = (
            {"context": lambda x: context_text, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
        
        response = chain.invoke(question)
        return response, docs
    except Exception as e:
        return f"Error calling Gemini Pro: {e}", docs

# Chat Input
if prompt := st.chat_input("What is the treatment for hypertension?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text, source_docs = get_answer(prompt)
            st.markdown(response_text)
            
            # Show sources in an expander
            if source_docs:
                with st.expander("View Source Documents"):
                    for i, doc in enumerate(source_docs):
                        st.markdown(f"**Source {i+1}** ({doc.metadata.get('filename', 'Unknown')}):")
                        st.text(doc.page_content)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response_text})
