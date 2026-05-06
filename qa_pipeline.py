import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class QAPipeline:
    """
    Handles the Question Answering pipeline using RAG.
    """
    def __init__(self, vector_store, model_name="gemini-flash-latest"):
        """
        Initialize the QA pipeline.
        
        Args:
            vector_store: The FAISS vector store instance.
            model_name (str): The Google model to use.
        """
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        
        # General Healthcare Assistant Prompt
        prompt_template = """You are a comprehensive Healthcare Assistant. Your role is to answer ANY health-related question based on the medical knowledge base provided.

**YOU CAN ANSWER QUESTIONS ABOUT:**
- Medical conditions and diseases
- Symptoms and causes
- Medications and treatments
- Lab test results and reference ranges
- General health and wellness
- Medical reports and terminology

**IMPORTANT GUIDELINES:**
- Base your answer STRICTLY on the provided context.
- If the answer is not in the context, say: "I don't have information about that in my current knowledge base."
- DO NOT provide medical diagnosis.
- DO NOT prescribe medications.
- DO NOT replace professional medical advice.
- Explain medical terms in simple, patient-friendly language.
- When discussing lab values, always mention reference ranges if available in the context.

**Context (Retrieved Medical Knowledge):**
{context}

**User Question:**
{question}

**Answer:**
Provide a detailed, educational answer. Include specific data points (like normal ranges) from the context if relevant.
    
**Disclaimer:**
This information is for educational purposes only and does not constitute medical advice. Please consult with your healthcare provider for personalized medical guidance.
"""
        
        self.PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.PROMPT}
        )

    def answer_question(self, query, file_context=""):
        """
        Answer a user question using the RAG pipeline.
        """
        # 1. Similarity Search with Scores (Manual Retrieval for Filtering)
        # Low scores are better in FAISS (L2 distance)
        docs_and_scores = self.retriever.vectorstore.similarity_search_with_score(query, k=5)
        
        # 2. Filter out noisy sources (Thresholding)
        # Values > 0.8 are often irrelevant for this model
        filtered_docs = [doc for doc, score in docs_and_scores if score < 0.75]
        
        input_dict = {"query": query}
        
        if file_context:
            # Smart prompt that handles unrelated questions
            special_template = f"""You are a comprehensive Healthcare Assistant.

**CONTEXT HANDLING INSTRUCTION (CRITICAL):**
Analyze the UPLOADED DOCUMENT context vs GENERAL MEDICAL KNOWLEDGE.
- If the question is about the uploaded document (e.g. "are my levels ok", "analyze this report") -> **Prioritize the document**.
- If the question is general -> **Use general knowledge**.
- **DO NOT** mention or cite general sources if they are irrelevant to the specific user enquiry.

**UPLOADED DOCUMENT CONTEXT:**
{file_context[:15000]}

**GENERAL MEDICAL KNOWLEDGE (FROM DATABASE):**
{{context}}

**User Question:**
{{question}}

**Answer:**
Provide a detailed answer. Only cite a source if it truly provided information for this answer.
"""
            special_prompt = PromptTemplate(
                template=special_template, input_variables=["context", "question"]
            )
            
            # Temporary chain with filtered docs only
            # We bypass the retriever to use our filtered list
            from langchain.chains.combine_documents import create_stuff_documents_chain
            from langchain.chains import create_retrieval_chain
            
            # We'll use the LLM directly with the prompt for better control
            chain = (
                {"context": lambda x: "\n\n".join([d.page_content for d in filtered_docs]), 
                 "question": lambda x: x["query"]}
                | special_prompt
                | self.llm
            )
            
            from langchain_core.output_parsers import StrOutputParser
            response_text = (chain | StrOutputParser()).invoke(input_dict)
            
            # Construct final response object
            from langchain.schema import Document
            file_source = Document(
                page_content="(Content from your uploaded report)",
                metadata={"source": "Your Uploaded Document", "filename": "Latest Report"}
            )
            
            # Only include general sources if they weren't filtered out
            all_sources = [file_source] + filtered_docs
            
            return {
                "result": response_text,
                "source_documents": all_sources
            }
            
        return self.qa_chain.invoke(input_dict)
