from rag.vector_store import VectorStoreManager

def test_retrieval():
    print("Testing retrieval...")
    try:
        vs_manager = VectorStoreManager(index_path="faiss_index")
        vector_store = vs_manager.load_vector_store()
        
        query = "What is the treatment for hypertension?"
        results = vector_store.similarity_search(query, k=2)
        
        print(f"Query: {query}")
        print(f"Found {len(results)} results:")
        for i, doc in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"Source: {doc.metadata.get('filename')}")
            print(f"Content: {doc.page_content[:200]}...") # truncate
            
        print("\nRetrieval test passed!")
    except Exception as e:
        print(f"Retrieval test failed: {e}")

if __name__ == "__main__":
    test_retrieval()
