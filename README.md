# 🏥 Healthcare RAG Assistant

An intelligent healthcare assistant that answers medical questions using your own documents (PDFs, TXT, etc.) and Google Gemini Pro.

## Features
- **Retrieval-Augmented Generation (RAG)**: Answers are based *strictly* on your documents.
- **Google Gemini Pro**: Powerful and fast understanding of medical text.
- **FAISS Vector Store**: Fast and efficient document search.
- **Google Drive Integration**: Import documents directly from a Drive folder.

---

## 🚀 Backend Quick Start Guide

### 1. Prerequisites
- **Python 3.9+** installed.
- A **Google Cloud API Key** (for Gemini). Get it [here](https://aistudio.google.com/app/apikey).
- (Optional) **Google Drive API Credentials** (`credentials.json`) if you want to import from Drive.

### 2. Installation
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/samichi-rungta/Healthcare-RAG.git
    cd Healthcare-RAG
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your API Key**:
    Create a file named `.env` in the main folder and add your key:
    ```
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

### 3. Usage (Streamlit / API)

#### Start the App
Run the following command to launch the interface:
```bash
streamlit run app/main.py
```

#### How to Add Documents
You have two ways to add knowledge:
1.  **Upload Manually**: Use the sidebar in the app to upload PDF or TXT files.
2.  **Google Drive**: 
    -   Place your `credentials.json` file in the project folder.
    -   Enter your Google Drive Folder ID in the sidebar.
    -   Click **"Start Drive Ingestion"**.

#### Asking Questions
Once documents are added (ingested), simply type your question in the chat box!
- *"What are the symptoms of hypertension?"*
- *"Summarize the patient's lab results."*

---

## 🛠️ Project Structure
- `app/`: Streamlit application code.
- `rag/`: Core RAG logic (ingestion, retrieval, QA).
- `data/`: Folder for storing raw data.
- `faiss_index/`: Local database storing your document embeddings.
- `src/`: React Frontend source code.

---

## ⚛️ Frontend Development (React + Vite)

This project also includes a modern React frontend.

### Getting Started

1.  **Install Node Dependencies**:
    ```bash
    npm install
    ```

2.  **Run Development Server**:
    ```bash
    npm run dev
    ```

### ESLint Configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
