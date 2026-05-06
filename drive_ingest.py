import os
import io
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from langchain_core.documents import Document
from .chunking import TextChunker
from .vector_store import VectorStoreManager
import pypdf

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    """Shows basic usage of the Drive v3 API."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("No credentials.json found.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def ingest_from_drive_folder(folder_id):
    """
    Ingests all supported files from a specific Google Drive folder.
    Streams content to memory, chunks it, and saves to ChromaDB.
    """
    service = get_drive_service()
    if not service:
        return False, "Authentication failed. Please ensure 'credentials.json' is in the project root."

    try:
        # Search for files in the folder
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(
            q=query, pageSize=1000, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])

        if not items:
            return True, "No files found in the specified folder."

        print(f"Found {len(items)} files in Google Drive folder.")
        
        vector_store_manager = VectorStoreManager(index_path="faiss_index")
        chunker = TextChunker()
        
        processed_count = 0
        
        for item in items:
            file_id = item['id']
            file_name = item['name']
            mime_type = item['mimeType']
            
            print(f"Processing {file_name} ({mime_type})...")
            
            file_content = ""
            
            # Download file content
            if mime_type == 'application/vnd.google-apps.document':
                request = service.files().export_media(fileId=file_id, mimeType='text/plain')
                response = request.execute()
                file_content = response.decode('utf-8')
            elif 'pdf' in mime_type or file_name.lower().endswith('.pdf'):
                request = service.files().get_media(fileId=file_id)
                content = request.execute()
                try:
                    reader = pypdf.PdfReader(io.BytesIO(content))
                    for page in reader.pages:
                        file_content += page.extract_text() + "\n"
                except Exception as e:
                    print(f"Failed to parse PDF {file_name}: {e}")
                    continue
            else:
                 # Standard download for text-based files
                 request = service.files().get_media(fileId=file_id)
                 content = request.execute()
                 try:
                    file_content = content.decode('utf-8')
                 except:
                    print(f"Could not decode {file_name} as text.")
                    continue

            if not file_content:
                continue
                
            # Create Document
            doc = Document(
                page_content=file_content,
                metadata={"source": f"gdrive://{file_id}", "filename": file_name}
            )
            
            # Chunk
            chunks = chunker.split_documents([doc])
            
            # Add to Vector Store (Incremental)
            if not os.path.exists("faiss_index"):
                 vector_store_manager.create_vector_store(chunks)
            else:
                 vector_store_manager.add_documents(chunks)
            
            processed_count += 1
            
        return True, f"Successfully processed {processed_count} files from Google Drive."

    except Exception as e:
        return False, f"Google Drive Error: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m rag.drive_ingest <folder_id>")
    else:
        folder_id = sys.argv[1]
        print(f"Ingesting from Folder ID: {folder_id}")
        success, msg = ingest_from_drive_folder(folder_id)
        print(msg)
