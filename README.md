# 🌱 Organic Farming RAG

A Retrieval-Augmented Generation (RAG) application that answers questions from the book:

Organic Farming: Cultivating Sustainable Agriculture

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