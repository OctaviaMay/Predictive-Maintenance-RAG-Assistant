from types import SimpleNamespace

import pytest

from src.pricing import calculate_cost, cost_breakdown


def test_gpt54_mini_cost():
    usage = SimpleNamespace(input_tokens=1_000_000, output_tokens=1_000_000)
    assert calculate_cost("gpt-5.4-mini", usage) == pytest.approx(0.75 + 4.50)


def test_unknown_model_raises():
    usage = SimpleNamespace(input_tokens=10, output_tokens=10)
    with pytest.raises(ValueError):
        calculate_cost("not-a-model", usage)


def test_breakdown_is_in_dollars():
    usage = SimpleNamespace(input_tokens=1_000_000, output_tokens=1_000_000)
    b = cost_breakdown("gpt-5.4-mini", usage)
    assert b["input_cost"] == pytest.approx(0.75)
    assert b["output_cost"] == pytest.approx(4.50)
    assert b["cost"] == pytest.approx(5.25)