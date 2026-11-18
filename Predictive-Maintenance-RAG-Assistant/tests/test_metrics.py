# tests/test_metrics.py
from types import SimpleNamespace
import pytest

from src.metrics import RAGWithMetrics

class FakeResponses:
    def create(self, **kwargs):
        return SimpleNamespace(
            output_text="answer",
            usage=SimpleNamespace(input_tokens=1000, output_tokens=200, total_tokens=1200),
        )


def test_llm_call_is_logged_with_cost():
    rag = RAGWithMetrics(index=None, llm_client=SimpleNamespace(responses=FakeResponses()),
                         instructions="i", prompt_template="{question}{context}", model="gpt-5.4-mini")
    assert rag.llm("prompt") == "answer"
    assert rag.last_call.total_tokens == 1200
    assert rag.last_call.cost == pytest.approx(0.00165)


class FakeIndex:
    def search(self, query, top_k=5):
        return [{"section": "Power Failure", "question": "Q?",
                 "answer": "Power outside 3500-9000 W triggers failure."}]

def test_rag_keeps_retrieved_context():
    rag = RAGWithMetrics(index=FakeIndex(),
                        llm_client=SimpleNamespace(responses=FakeResponses()),
                        instructions="i", prompt_template="{question}\n{context}",
                        model="gpt-5.4-mini")
    rag.rag("why power failure?")
    assert "3500-9000 W" in rag.last_context