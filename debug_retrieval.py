
import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

def debug_retrieval(query, k=5):
    print(f"--- Debugging Retrieval for: '{query}' (k={k}) ---")
    
    embeddings = get_embeddings()
    try:
        vector_store = FAISS.load_local(
            folder_path="faiss_index", 
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        print(f"Error loading index: {e}")
        return

    # specific search
    docs_and_scores = vector_store.similarity_search_with_score(query, k=k)
    
    print(f"Found {len(docs_and_scores)} documents:\n")
    
    for i, (doc, score) in enumerate(docs_and_scores):
        print(f"Result {i+1} (Score: {score:.4f}):")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Content Preview: {doc.page_content[:200]}...")  # Show first 200 chars
        print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "I get constipated a lot and dont poop for 3-4 days straight sometimes is that ok"
    
    debug_retrieval(query)
