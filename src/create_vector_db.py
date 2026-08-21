import os
import glob
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from load_pdf import load_and_split_pdf
from rag import EMBEDDING_CACHE_DIR, EMBEDDING_LOCAL_ONLY, EMBEDDING_MODEL


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.getenv(
    "VECTOR_DB_PATH", os.path.join(BASE_DIR, "vectorstore", "chroma_db")
)


def create_vector_database():
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    if not pdf_files:
        raise RuntimeError("No PDF files found in the data directory.")

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
            raise RuntimeError(f"Could not load {pdf_path}: {e}") from e

    if not all_chunks:
        raise RuntimeError("No document chunks were created from the supplied PDFs.")

    print(f"Total {len(all_chunks)} chunks to embed.")

    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        cache_folder=EMBEDDING_CACHE_DIR,
        model_kwargs={"local_files_only": EMBEDDING_LOCAL_ONLY},
        encode_kwargs={"normalize_embeddings": True},
    )

    db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embedding_model,
        persist_directory=DB_PATH
    )

    indexed_chunks = db._collection.count()
    if indexed_chunks != len(all_chunks):
        raise RuntimeError(
            f"Database validation failed: expected {len(all_chunks)} chunks, "
            f"but found {indexed_chunks}."
        )

    print(f"Vector Database Created Successfully with {indexed_chunks} chunks.")
    return indexed_chunks


if __name__ == "__main__":
    create_vector_database()
