import os
import time
from rag.ingest import ingest_file

DATA_DIR = "data/HealthcareDocus"
INDEX_FILE = "faiss_index/index.faiss"

def main():
    if not os.path.exists(INDEX_FILE):
        print("Error: No existing FAISS index found at 'faiss_index/index.faiss'.")
        print("Please run 'python process_data.py' first to build the initial index.")
        return

    last_ingest_time = os.path.getmtime(INDEX_FILE)
    print(f"Checking for files added after last ingestion: {time.ctime(last_ingest_time)}")
    
    new_files = []
    
    # Walk through the directory for new/modified files
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.startswith('.'): continue # Skip hidden files
            
            file_path = os.path.join(root, file)
            
            # Check modification time
            # We buffer by 1 second to avoid edge cases
            if os.path.getmtime(file_path) > (last_ingest_time + 1):
                new_files.append(file_path)
    
    if not new_files:
        print("\nNo new or modified files found in 'data/HealthcareDocus'.")
        print("If you just added a file, ensure it is in the correct folder.")
        return

    print(f"\nFound {len(new_files)} new files to ingest:")
    for f in new_files:
        print(f" - {os.path.basename(f)}")
        
    print("\nStarting incremental ingestion...")
    print("(This only processes the new files, so it will be fast!)")
    
    count = 0
    for f in new_files:
        try:
            print(f"Ingesting: {os.path.basename(f)}...")
            success, msg = ingest_file(f)
            if success:
                print(f"  [SUCCESS] {msg}")
                count += 1
            else:
                print(f"  [FAILED] {msg}")
        except Exception as e:
            print(f"  [ERROR] {e}")
            
    if count > 0:
        print(f"\nDone! Successfully added {count} files to the knowledge base.")
        print("Please restart your Streamlit app to load the updated index.")
    else:
        print("\nNo files were successfully ingested.")

if __name__ == "__main__":
    main()
