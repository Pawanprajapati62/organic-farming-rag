# 🌱 Organic Farming Assistant using RAG

A Streamlit application that answers organic-farming questions using retrieved passages from local PDFs and Gemini.

## Runtime requirements

- Python 3.11
- A Google AI Studio API key
- Internet access during the first embedding-model download and database build

Dependencies are defined in `pyproject.toml` and locked in `uv.lock`. Use `uv` for all installs and runs so local and production environments use the same versions.

## Local setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Copy `.env.example` to `.env` and set `GOOGLE_API_KEY`.
3. Install the locked dependencies:

   ```bash
   uv sync --frozen --no-dev
   ```

4. Build the searchable knowledge base:

   ```bash
   uv run python rebuild_db.py
   ```

5. Start the application:

   ```bash
   uv run streamlit run app.py
   ```

## Docker deployment

Docker Compose provides a production-like local deployment with a persistent `rag-data` volume for the Chroma database and embedding cache.
The container initializes that volume with the app user's permissions automatically.

1. Copy `.env.example` to `.env` and add `GOOGLE_API_KEY`.
2. Build the image:

   ```bash
   docker compose build
   ```

3. Build the database once (or after changing the PDFs):

   ```bash
   docker compose run --rm app uv run --no-sync python rebuild_db.py
   ```

4. Start the service:

   ```bash
   docker compose up -d
   ```

Open `http://localhost:8501`.

For a hosted deployment, supply `GOOGLE_API_KEY` through the platform's secret manager, expose the platform-provided `PORT`, and attach a read/write persistent volume at `/data`. Never commit `.env`, `vectorstore`, or `.cache`.
Do not share the output of `docker compose config`, because it expands environment values and can reveal secrets.

## Project structure

- `Docs/` — source PDFs
- `src/` — retrieval and database-building code
- `vectorstore/` — local Chroma data (generated; not committed)
- `rebuild_db.py` — atomically rebuilds the database
- `app.py` — Streamlit user interface

## Features

- PDF question answering with source-page citations
- Chroma vector database
- Hugging Face embeddings
- Gemini answers and follow-up questions
- Streamlit interface
