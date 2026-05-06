import os
import glob
from typing import List
from langchain_core.documents import Document
from rag.chunking import TextChunker
from rag.vector_store import VectorStoreManager
import pypdf

def load_documents(data_dir: str) -> List[Document]:
    """
    Loads documents from the specified directory.
    Supports .txt, .json, .csv, and .pdf.
    """
    documents = []
    
    # Walk through the directory and subdirectories
    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # Filter for supported files
            if not file.lower().endswith(('.txt', '.json', '.csv', '.md', '.pdf')):
                continue
                
            try:
                content = ""
                if file.lower().endswith('.pdf'):
                    reader = pypdf.PdfReader(file_path)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                # Create a Document object
                doc = Document(
                    page_content=content,
                    metadata={"source": file_path, "filename": file}
                )
                documents.append(doc)
            except Exception as e:
                print(f"Failed to load {file}: {e}")
                
    return documents

def ingest_data():
    """
    Main function to load, chunk, and index data.
    """
    print("Starting data ingestion...")
    
    base_data_path = "data"
    chunks_dir = "faiss_index"
    
    # Check current directory to ensure paths are correct
    if not os.path.exists(base_data_path):
        print(f"Error: {base_data_path} not found. Running from: {os.getcwd()}")
        return

    # 1. Load Documents
    print(f"Loading documents from '{base_data_path}' directory...")
    raw_docs = load_documents(base_data_path)
    if not raw_docs:
        print("No documents found in 'data' directory. Please run generate_data.py first.")
        # Try running generation if empty? No, let's just fail for now as per logic, or process_data.py handles it.
        return

    print(f"Loaded {len(raw_docs)} documents.")

    # 2. Chunk Documents
    print("Chunking documents...")
    chunker = TextChunker()
    chunked_docs = chunker.split_documents(raw_docs)
    print(f"Created {len(chunked_docs)} chunks.")

    # 3. Index Documents
    print(f"Indexing documents to '{chunks_dir}'...")
    # Initialize VectorStoreManager
    vector_store_manager = VectorStoreManager(index_path=chunks_dir)
    
    # Create and save the vector store
    vector_store_manager.create_vector_store(chunked_docs)
    
    print(f"Ingestion complete. Vector store saved to '{chunks_dir}'.")

def ingest_file(file_path: str):
    """
    Ingests a single file into the vector store.
    Used for on-the-fly uploads.
    """
    print(f"Ingesting file: {file_path}")
    
    # 1. Load Single Document
    try:
        content = ""
        if file_path.lower().endswith('.pdf'):
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                content += page.extract_text() + "\n"
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
        doc = Document(
            page_content=content,
            metadata={"source": file_path, "filename": os.path.basename(file_path)}
        )
        
        # 2. Chunk
        chunker = TextChunker()
        chunks = chunker.split_documents([doc])
        
        # 3. Add to Index
        vector_store_manager = VectorStoreManager(index_path="faiss_index")
        # Ensure db exists or create it
        if not os.path.exists("faiss_index"):
             vector_store_manager.create_vector_store(chunks)
        else:
             vector_store_manager.add_documents(chunks)
             
        return True, f"Successfully processed {len(chunks)} chunks."
        
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    ingest_data()
