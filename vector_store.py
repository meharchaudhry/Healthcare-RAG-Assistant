import os
from langchain_community.vectorstores import FAISS
from .embeddings import get_embeddings

class VectorStoreManager:
    """
    Manages the FAISS vector store.
    Supports creation, saving, and loading of indexes.
    """
    def __init__(self, index_path="faiss_index"):
        self.index_path = index_path
        self.embeddings = get_embeddings()

    def create_vector_store(self, documents):
        """
        Creates a new FAISS vector store from documents and saves it locally.
        """
        if not documents:
            return None
            
        vector_store = FAISS.from_documents(
            documents=documents, 
            embedding=self.embeddings
        )
        
        # Save to disk
        vector_store.save_local(self.index_path)
            
        return vector_store

    def load_vector_store(self):
        """
        Loads an existing FAISS vector store.
        """
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"Index not found at {self.index_path}")
            
        return FAISS.load_local(
            folder_path=self.index_path, 
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True
        )

    def add_documents(self, documents):
        """
        Adds new documents to the existing vector store.
        """
        if not documents:
            return
            
        vector_store = self.load_vector_store()
        vector_store.add_documents(documents)
        vector_store.save_local(self.index_path)

