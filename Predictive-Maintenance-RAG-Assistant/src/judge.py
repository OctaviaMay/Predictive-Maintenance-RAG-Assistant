import json
from pydantic import BaseModel
from typing import Literal
from openai import OpenAI

from src.evaluation import get_llm_response_retry
from src.pricing import calculate_cost
import time

JUDGE_MODEL = "gpt-5.4-mini"

class JudgeVerdict(BaseModel):
    relevance:Literal["NON_RELEVANT","PARTIAL_RELEVANT","RELEVANT"]
    groundedness:Literal["NON_GROUNDED", "PARTIALLY_GROUNDED", "GROUNDED"]
    unsupported_claims:list[str]
    explanation: str

judge_instructions = """
You are an expert evaluator for a retrieval-augmented maintenance assistant.
You receive a QUESTION, the retrieved CONTEXT, and the assistant's ANSWER.
Evaluate two things independently.

1. Relevance: does the answer address the question?
- RELEVANT: the answer addresses the question
- PARTIAL_RELEVANT: the answer partially addresses the question
- NON_RELEVANT: the answer does not address the question

2. Groundedness: is every factual claim in the answer supported by the CONTEXT?
Judge only against the CONTEXT, not your own knowledge. A claim that may be
true in general but does not appear in the context counts as unsupported.
- GROUNDED: all factual claims are supported by the context
- PARTIALLY_GROUNDED: most claims are supported, but at least one is not
- NOT_GROUNDED: the main claims are unsupported or contradict the context

If the answer correctly says the context lacks enough information, it is GROUNDED.
Generic advice (e.g. "follow your site's safety procedure") is not an
unsupported claim unless it states specific facts such as numbers,
thresholds, causes or intervals.

List each unsupported claim in unsupported_claims, quoted or closely
paraphrased from the answer. Use an empty list if there are none.
""".strip()

judge_prompt = """
QUESTION: {question}

CONTEXT: {context}

ANSWER: {answer}
""".strip()


def evaluate_answer(question, answer, context,client=None):
    """ Judge one answer for relevance and groundedness in a single LLM call."""
    if client is None:
        client = OpenAI()

    prompt = judge_prompt.format(
        question = question,
        context = context,
        answer = answer
    )

    start_time = time.time()
    result, usage =get_llm_response_retry(client, 
                           judge_instructions,
                           prompt,
                           JudgeVerdict,JUDGE_MODEL)
    response_time = time.time() - start_time

    cost = calculate_cost(JUDGE_MODEL, usage)

    return {
        "relevance": result.relevance,
        "groundedness" : result.groundedness,
        "unsupported_claims" : result.unsupported_claims,
        "explanation": result.explanation,
        "model": JUDGE_MODEL,
        "prompt_tokens" : usage.input_tokens,
        "completion_tokens" : usage.output_tokens,
        "total_tokens" : usage.total_tokens,
        "response_time" : response_time,
        "cost" : cost
    }
    
