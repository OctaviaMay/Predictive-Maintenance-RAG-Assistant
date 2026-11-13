from types import SimpleNamespace

import pytest

from src.judge import RelevanceVerdict, evaluate_relevance


class FakeResponses:
    def parse(self, **kwargs):
        return SimpleNamespace(
            output_parsed=RelevanceVerdict(relevance="RELEVANT", explanation="ok"),
            usage=SimpleNamespace(input_tokens=1000, output_tokens=200, total_tokens=1200),
        )


class FakeClient:
    responses = FakeResponses()


def test_judge_returns_verdict_and_cost():
    result = evaluate_relevance("q", "a", client=FakeClient())
    assert result["relevance"] == "RELEVANT"
    assert result["total_tokens"] == 1200
    assert result["cost"] == pytest.approx((1000 * 0.75 + 200 * 4.50) / 1_000_000)