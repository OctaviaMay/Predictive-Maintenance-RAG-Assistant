from types import SimpleNamespace

import pytest

from src.judge import JudgeVerdict, evaluate_answer

class FakeResponses:
    def __init__(self):
        self.last_kwargs = None

    def parse(self, **kwargs):
        self.last_kwargs = kwargs
        return SimpleNamespace(
            output_parsed=JudgeVerdict(relevance="RELEVANT", 
                                       groundedness = "PARTIALLY_GROUNDED",
                                       unsupported_claims = ["Replace the spindle every 500 hours"],
                                       explanation = "One interval is not in the context."),
            usage=SimpleNamespace(input_tokens=1000, output_tokens=200, total_tokens=1200),
        )


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()

def test_judge_receive_context():
    client = FakeClient()
    evaluate_answer("q", "a", "CONTEXT-MARKER", client=client)
    assert "CONTEXT-MARKER" in str(client.responses.last_kwargs["input"])

def test_judge_returns_groundedness_and_cost():
    result = evaluate_answer("q", "a", "ctx",client=FakeClient())
    assert result["relevance"] == "RELEVANT"
    assert result["groundedness"] == "PARTIALLY_GROUNDED"
    assert result["unsupported_claims"] == ["Replace the spindle every 500 hours"]
    assert result["response_time"] >= 0
    assert result["cost"] == pytest.approx((1000 * 0.75 + 200 * 4.50) / 1_000_000)