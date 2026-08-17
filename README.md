# 🌱 Organic Farming Assistant using RAG

A Retrieval-Augmented Generation (RAG) application that answers questions from the book:

Organic Farming: Cultivating Sustainable Agriculture

---

## Project Structure

OrganicAI/
├── Docs/                          ← Put your organic farming PDFs here
├── src/
│   ├── ingest.py                  ← Ingestion pipeline logic
│   └── ...
├── vectorstore/                   ← Auto-generated FAISS index
├── app.py                         ← Streamlit chat UI
├── main.py                        ← CLI entrypoint
├── rebuild_db.py                  ← Standalone vector store rebuild script
└── README.md

---

## Features

- PDF Question Answering
- Chroma Vector Database
- HuggingFace Embeddings
- Gemini 2.5 Flash
- Source Page Numbers
- Retrieved Context
- Streamlit Interface

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Add API Key

Create

```
.env
```

Add

```
GOOGLE_API_KEY=YOUR_KEY
```

---

## Build Vector Database

```bash
cd src

python create_vector_db.py
```

---

## Run

```bash
streamlit run app.py
```

---

# Rebuild the FAISS vector database from PDFs in Docs/
```bash
python rebuild_db.py
```

# Force rebuild over existing index files
```bash
python rebuild_db.py --force
```

# Custom docs directory or output vectorstore path
```bash
python rebuild_db.py --docs-dir ./my_pdfs --vectorstore-dir ./my_vectorstore
```
