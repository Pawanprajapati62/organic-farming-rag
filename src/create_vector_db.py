import os
import glob
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from load_pdf import load_and_split_pdf


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "vectorstore", "chroma_db")


def create_vector_database():
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    if not pdf_files:
        print("No PDF files found in data directory.")
        return

    all_chunks = []
    for pdf_path in pdf_files:
        print(f"Loading PDF: {os.path.basename(pdf_path)}...")
        try:
            chunks = load_and_split_pdf(pdf_path)
            # Tag metadata with file name
            for chunk in chunks:
                chunk.metadata["source_file"] = os.path.basename(pdf_path)
            all_chunks.extend(chunks)
            print(f"Added {len(chunks)} chunks from {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"Error loading {pdf_path}: {e}")

    print(f"Total {len(all_chunks)} chunks to embed.")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embedding_model,
        persist_directory=DB_PATH
    )

    print("Vector Database Created Successfully!")


if __name__ == "__main__":
    create_vector_database()


    