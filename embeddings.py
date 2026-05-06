import os
from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingModel:
    """
    Singleton class to handle the embedding model.
    Uses HuggingFaceEmbeddings with a lightweight, efficient model.
    """
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingModel, cls).__new__(cls)
            # Initialize the model once
            # all-MiniLM-L6-v2 is a good balance of speed and performance for CPU usage
            cls._model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'} # Force CPU for compatibility/ease of install
            )
        return cls._instance

    def get_embedding_model(self):
        """Returns the initialized embedding model."""
        return self._model

def get_embeddings():
    """Factory function to get the embedding model instance."""
    return EmbeddingModel().get_embedding_model()
