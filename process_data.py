import os
import subprocess
import sys

def main():
    print("=== Healthcare RAG Data Pipeline ===")
    
    # 1. Generate Data
    print("\n[Step 1] Generating Synthetic Data...")
    try:
        subprocess.run([sys.executable, "data/generate_data.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating data: {e}")
        return

    # 2. Ingest Data
    print("\n[Step 2] Ingesting Data into Vector Store...")
    try:
        # Run as a module to resolve imports correctly
        subprocess.run([sys.executable, "-m", "rag.ingest"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error ingesting data: {e}")
        return

    print("\n=== Pipeline Complete ===")
    print("You can now run the application using: streamlit run app/main.py")

if __name__ == "__main__":
    main()
