from backend.app.rag.vector_store import vector_store
from backend.app.rag.retriever import get_rag_context

def test_rag_indexing():
    vector_store.initialize()
    assert len(vector_store.chunks) > 0, "Vector store should have indexed chunks"
    
def test_rag_retrieval_breathing():
    context, sources = get_rag_context("I'm panicking and need a breathing technique", top_k=2)
    assert len(sources) > 0
    assert "[RETRIEVED_KNOWLEDGE_CONTEXT]" in context
    # Check if Box Breathing or Paced Breathing is found
    titles = [s["title"].lower() for s in sources]
    content = " ".join([s["content"].lower() for s in sources])
    assert any("breathing" in t or "breathing" in content for t in titles)

def test_rag_retrieval_cbt():
    context, sources = get_rag_context("I feel like an absolute failure and I'm catastrophizing", top_k=2)
    assert len(sources) > 0
    content = " ".join([s["content"].lower() for s in sources])
    assert "catastrophizing" in content or "cognitive" in content or "thought" in content

if __name__ == "__main__":
    test_rag_indexing()
    test_rag_retrieval_breathing()
    test_rag_retrieval_cbt()
    print("All RAG Tests Passed!")
