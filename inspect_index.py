from rag.vector_store import VectorStoreManager
import os

def list_files_in_index():
    try:
        vs = VectorStoreManager().load_vector_store()
        docstore = vs.docstore._dict  # FAISS docstore
        
        sources = set()
        total_chunks = len(docstore)
        
        for doc_id, doc in docstore.items():
            if 'source' in doc.metadata:
                sources.add(doc.metadata['source'])
                
        print(f"\n--- Index Statistics ---")
        print(f"Total Chunks: {total_chunks}")
        print(f"Total Unique Documents: {len(sources)}")
        
        # Optionally show sample files
        print("\nSample files in index:")
        for idx, src in enumerate(list(sources)[:10]):
            print(f" - {os.path.basename(src)}")
            
    except Exception as e:
        print(f"Error inspecting index: {e}")

if __name__ == "__main__":
    list_files_in_index()
