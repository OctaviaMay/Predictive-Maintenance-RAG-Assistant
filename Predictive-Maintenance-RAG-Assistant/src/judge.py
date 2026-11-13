import json
from pydantic import BaseModel
from typing import Literal
from openai import OpenAI

from src.evaluation import get_llm_response_retry
from src.pricing import calculate_cost
import time

JUDGE_MODEL = "gpt-5.4-mini"

class RelevanceVerdict(BaseModel):
    relevance:Literal['NON_RELEVANT','PARTIAL_RELEVANT','RELEVANT']
    explanation: str

judge_instructions = """
You are an expert evaluator for a RAG system.
Analyze the relevance of the generated answer to the given question.

Classify the answer as:
- RELEVANT: the answer addresses the question
- PARTIAL_RELEVANT: the answer partially addresses the question
- NON_RELEVANT: the answer does not address the question
""".strip()

judge_prompt = """
Question: {question}
Generated Answer: {answer}
""".strip()

def evaluate_relevance(question, answer, client=None):
    if client is None:
        client = OpenAI()

    prompt = judge_prompt.format(
        question = question,
        answer = answer
    )

    start_time = time.time()
    result, usage =get_llm_response_retry(client, 
                           judge_instructions,
                           prompt,
                           RelevanceVerdict,JUDGE_MODEL)
    response_time = time.time() - start_time

    cost = calculate_cost(JUDGE_MODEL, usage)

    return {
        "relevance": result.relevance,
        "explanation": result.explanation,
        "model": JUDGE_MODEL,
        "prompt_tokens" : usage.input_tokens,
        "completion_tokens" : usage.output_tokens,
        "total_tokens" : usage.total_tokens,
        "total_response_time" : response_time,
        "cost" : cost
    }
    
