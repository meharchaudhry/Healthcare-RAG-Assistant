import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Add the root directory to sys.path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.ingest import ingest_file
from rag.qa_pipeline import QAPipeline
from rag.vector_store import VectorStoreManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes and origins (for development)
CORS(app, resources={r"/*": {"origins": "*"}})

# Helper to get QA Pipeline (lazy loading or global)
# Global variable for caching
_QA_PIPELINE = None

def get_qa_pipeline():
    global _QA_PIPELINE
    if _QA_PIPELINE is not None:
        return _QA_PIPELINE
        
    try:
        if not os.path.exists("faiss_index"):
            return None
        
        vector_store_manager = VectorStoreManager()
        vector_store = vector_store_manager.load_vector_store()
        _QA_PIPELINE = QAPipeline(vector_store)
        logger.info("QA Pipeline loaded and cached.")
        return _QA_PIPELINE
    except Exception as e:
        logger.error(f"Error loading QA pipeline: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Healthcare RAG API"}), 200

# Global variable for latest uploaded context (simple in-memory storage)
_LAST_UPLOADED_CONTEXT = ""

@app.route('/upload', methods=['POST'])
def upload_document():
    global _LAST_UPLOADED_CONTEXT
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        try:
            # Save to temp file
            save_dir = "data/patient_uploads"
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, file.filename)
            file.save(file_path)
            
            # Extract text immediately for current session context
            content = ""
            try:
                if file_path.lower().endswith('.pdf'):
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
                elif file_path.lower().endswith('.txt'):
                     with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                
                # Store in global context (limit to 10k chars to be safe)
                _LAST_UPLOADED_CONTEXT = content[:15000]
                logger.info(f"Captured context from {file.filename} ({len(_LAST_UPLOADED_CONTEXT)} chars)")
            except Exception as e:
                logger.error(f"Failed to extract text for context injection: {e}")

            # Ingest (Background Indexing)
            # We clear the pipeline cache so the new file is eventually indexed properly
            global _QA_PIPELINE
            _QA_PIPELINE = None
            
            success, msg = ingest_file(file_path)
            
            if success:
                return jsonify({
                    "message": f"Successfully processed {file.filename}", 
                    "details": msg,
                    "analysis_ready": True
                }), 200
            else:
                return jsonify({"error": f"Ingestion failed: {msg}"}), 500
                
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    global _LAST_UPLOADED_CONTEXT
    
    data = request.json
    if not data or 'question' not in data:
        return jsonify({"error": "Missing 'question' in request body"}), 400
    
    question = data['question']
    
    qa_pipeline = get_qa_pipeline()
    if not qa_pipeline:
        return jsonify({
            "answer": "Knowledge base not found. Please upload a document first.",
            "sources": []
        }), 200
        
    try:
        # Pass the specific file context if available
        response = qa_pipeline.answer_question(question, file_context=_LAST_UPLOADED_CONTEXT)
        
        # Format sources
        sources = []
        if "source_documents" in response:
            for doc in response["source_documents"]:
                sources.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata
                })
        
        return jsonify({
            "answer": response["result"],
            "sources": sources
        }), 200
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
