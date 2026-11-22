import os
import glob
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.app.core.config import settings

logger = logging.getLogger("emotional_chatbot.rag")

class DocumentChunk:
    def __init__(self, doc_name: str, title: str, content: str, embedding: Optional[List[float]] = None):
        self.doc_name = doc_name
        self.title = title
        self.content = content
        self.embedding = embedding

class SimpleVectorStore:
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self._is_initialized = False

    def chunk_markdown(self, file_path: Path) -> List[DocumentChunk]:
        """Splits markdown file into meaningful sub-sections by headers."""
        chunks = []
        doc_name = file_path.name
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split by markdown headers ## or ###
            sections = content.split("\n## ")
            doc_title = sections[0].replace("# ", "").strip() if sections else doc_name

            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                header = section.split("\n")[0].strip()
                chunk_title = f"{doc_title} - {header}" if i > 0 else doc_title
                chunk_body = section.strip()
                chunks.append(DocumentChunk(doc_name=doc_name, title=chunk_title, content=chunk_body))
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
        return chunks

    def compute_embedding(self, text: str) -> Optional[List[float]]:
        """Generates embedding using Gemini API if key is available, else returns None."""
        if not settings.GEMINI_API_KEY:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            result = genai.embed_content(
                model=settings.GEMINI_EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_query"
            )
            return result["embedding"]
        except Exception as e:
            logger.debug(f"Gemini embedding API call failed: {e}")
            return None

    def initialize(self):
        """Loads and indexes knowledge documents."""
        if self._is_initialized and self.chunks:
            return

        docs_dir = settings.KNOWLEDGE_DOCS_DIR
        md_files = list(docs_dir.glob("*.md"))
        logger.info(f"Indexing {len(md_files)} knowledge base documents from {docs_dir}")

        all_chunks = []
        for file_path in md_files:
            file_chunks = self.chunk_markdown(file_path)
            all_chunks.extend(file_chunks)

        self.chunks = all_chunks
        self._is_initialized = True
        logger.info(f"RAG Knowledge Store initialized with {len(self.chunks)} chunks.")

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant chunks using semantic search with lexical fallback."""
        if not self.chunks:
            self.initialize()
            
        if not self.chunks:
            return []

        query_embedding = self.compute_embedding(query)
        scored_chunks = []

        if query_embedding is not None:
            # Semantic cosine similarity
            q_vec = np.array(query_embedding)
            q_norm = np.linalg.norm(q_vec)
            for chunk in self.chunks:
                if chunk.embedding is None:
                    chunk.embedding = self.compute_embedding(chunk.content)
                if chunk.embedding is not None:
                    c_vec = np.array(chunk.embedding)
                    c_norm = np.linalg.norm(c_vec)
                    similarity = float(np.dot(q_vec, c_vec) / (q_norm * c_norm + 1e-9))
                    scored_chunks.append((similarity, chunk))
        
        # If semantic embeddings were unavailable or yielded no scores, use token-overlap BM25-style scoring
        if not scored_chunks:
            query_words = set(re_tokenize(query.lower()))
            for chunk in self.chunks:
                chunk_words = re_tokenize(chunk.content.lower())
                if not chunk_words:
                    continue
                overlap = sum(1 for w in query_words if w in chunk_words)
                # Boost if title matches
                title_overlap = sum(2 for w in query_words if w in chunk.title.lower())
                score = (overlap + title_overlap) / (len(chunk_words) ** 0.5 + 1e-5)
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_results = []
        for score, chunk in scored_chunks[:top_k]:
            top_results.append({
                "title": chunk.title,
                "doc_name": chunk.doc_name,
                "content": chunk.content,
                "score": round(float(score), 4)
            })
        return top_results

def re_tokenize(text: str) -> List[str]:
    import re
    return re.findall(r"\b[a-zA-Z]{3,}\b", text)

# Global singleton
vector_store = SimpleVectorStore()
