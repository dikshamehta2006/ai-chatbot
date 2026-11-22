import logging
from typing import List, Dict, Any, Tuple
from backend.app.rag.vector_store import vector_store

logger = logging.getLogger("emotional_chatbot.rag")

def get_rag_context(query: str, top_k: int = 2) -> Tuple[str, List[Dict[str, Any]]]:
    """Retrieves relevant knowledge chunks and returns a formatted prompt block + raw metadata."""
    if not query or not query.strip():
        return "", []

    results = vector_store.search(query=query, top_k=top_k)
    if not results:
        return "", []

    context_lines = ["[RETRIEVED_KNOWLEDGE_CONTEXT]"]
    for i, res in enumerate(results, 1):
        context_lines.append(f"--- Reference {i}: {res['title']} ---")
        context_lines.append(res['content'])
        context_lines.append("")
    context_lines.append("[END_RETRIEVED_KNOWLEDGE_CONTEXT]")

    formatted_context = "\n".join(context_lines)
    return formatted_context, results
