import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.qa_pipeline import QAPipeline
from rag.vector_store import VectorStoreManager

def test_rag_system():
    print("=== Testing Healthcare RAG System ===")
    
    # 1. Initialize Vector Store
    print("Loading vector store...")
    vector_store_manager = VectorStoreManager(index_path="faiss_index")
    vector_store = vector_store_manager.load_vector_store()
    
    if not vector_store:
        print("Error: Could not load vector store. Did you run process_data.py?")
        return

    # 2. Initialize Pipeline
    print("Initializing QA Pipeline...")
    qa_pipeline = QAPipeline(vector_store)
    
    # 3. Test Questions (Patient-Facing)
    questions = [
        "What does a high ALT level mean in a blood test?",
        "I have a sharp pain in my lower right abdomen, what could it be?",
        "What is the normal range for Hemoglobin A1c?",
        "Explain the difference between Type 1 and Type 2 Diabetes.",
        "What are the side effects of Lisinopril?",
    ]
    
    for q in questions:
        print(f"\n[Question]: {q}")
        try:
            result = qa_pipeline.answer_question(q)
            print(f"[Answer]:\n{result['result']}")
            print("-" * 50)
            
            # Check sources
            print("Sources used:")
            for doc in result['source_documents']:
                source = doc.metadata.get('filename', 'Unknown')
                print(f" - {source}")
                
        except Exception as e:
            print(f"Error answering question: {e}")

if __name__ == "__main__":
    test_rag_system()
