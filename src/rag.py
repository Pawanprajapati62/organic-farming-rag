import os
from dotenv import load_dotenv

# Streamlit Cloud Secrets Fallback
try:
    import streamlit as st
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "vectorstore", "chroma_db")


class OrganicRAG:

    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.reload_db()

    def reload_db(self):
        self.vector_db = Chroma(
            persist_directory=DB_PATH,
            embedding_function=self.embedding_model
        )

    def get_stats(self):
        try:
            count = self.vector_db._collection.count()
            return {"total_chunks": count}
        except Exception:
            return {"total_chunks": 0}

    def ask(self, question, top_k=5, temperature=0.0):
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            temperature=temperature
        )

        results = self.vector_db.similarity_search_with_score(
            query=question,
            k=top_k
        )

        docs = [doc for doc, score in results]

        context_parts = []
        for i, (doc, score) in enumerate(results, 1):
            src_file = doc.metadata.get("source_file", doc.metadata.get("source", "Organic Farming Guide"))
            page_num = doc.metadata.get("page", 0) + 1
            context_parts.append(
                f"[Chunk {i} | File: {os.path.basename(src_file)} | Page {page_num}]\n{doc.page_content}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are an expert Organic Farming AI Consultant.

Answer the user's question accurately, clearly, and comprehensively based strictly on the provided context.
If the requested information is not available in the context, respond with:
"I couldn't find this information in the provided organic farming documents."

Context:
{context}

User Question:
{question}

Response Guidelines:
1. Format your answer nicely using Markdown (use bold text, bullet points, and clean headings where applicable).
2. At the end of your response, provide exactly 3 relevant, interesting follow-up questions the user might want to ask next to explore the topic further.
Format the follow-up section strictly as:

### Follow-up Questions:
- Question 1?
- Question 2?
- Question 3?
"""

        response = llm.invoke(prompt)
        content = response.text

        follow_ups = []
        answer = content
        if "### Follow-up Questions:" in content:
            parts = content.split("### Follow-up Questions:")
            answer = parts[0].strip()
            raw_lines = parts[1].strip().split("\n")
            for line in raw_lines:
                cleaned = line.strip().lstrip("-*123456789. ").strip()
                if cleaned and len(cleaned) > 5:
                    follow_ups.append(cleaned)

        pages = sorted(
            set(
                doc.metadata.get("page", 0) + 1
                for doc in docs
            )
        )

        sources = []
        for doc, score in results:
            dist = float(score)
            match_pct = max(55, min(99, int((1.0 - (dist / 2.5)) * 100)))
            src_file = os.path.basename(doc.metadata.get("source_file", doc.metadata.get("source", "Document")))
            sources.append(
                {
                    "page": doc.metadata.get("page", 0) + 1,
                    "file": src_file,
                    "text": doc.page_content,
                    "score": round(dist, 4),
                    "confidence": match_pct
                }
            )

        return {
            "answer": answer,
            "follow_ups": follow_ups[:3],
            "pages": pages,
            "sources": sources
        }


