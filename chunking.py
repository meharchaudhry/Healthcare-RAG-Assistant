from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextChunker:
    """
    Handles the chunking of text documents into smaller pieces for embedding.
    """
    def __init__(self, chunk_size=500, chunk_overlap=50):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size (int): The maximum size of each chunk.
            chunk_overlap (int): The amount of overlap between chunks.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_documents(self, documents):
        """
        Split a list of documents into chunks.
        
        Args:
            documents (List[Document]): List of langchain Document objects.
            
        Returns:
            List[Document]: List of chunked Document objects.
        """
        return self.splitter.split_documents(documents)

    def split_text(self, text):
        """
        Split a raw string into chunks.
        
        Args:
            text (str): Raw text string.
            
        Returns:
            List[str]: List of text chunks.
        """
        return self.splitter.split_text(text)
